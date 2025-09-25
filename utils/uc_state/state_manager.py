"""
UC-State: Unity Catalog-based state management utility
Manages Databricks resource state using Unity Catalog tables.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import CatalogInfo, SchemaInfo
import logging

logger = logging.getLogger(__name__)


class UCState:
    """Unity Catalog-based state management for Databricks resources."""
    
    def __init__(self, catalog: str, schema: str = "_caspers_state", table: str = "resources"):
        """
        Initialize UC-State manager.
        
        Args:
            catalog: The catalog name to store state in
            schema: Schema name (default: _caspers_state)  
            table: Table name (default: resources)
        """
        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.full_table_name = f"{catalog}.{schema}.{table}"
        self.w = WorkspaceClient()
        
        self._ensure_catalog_schema_table()
    
    def _ensure_catalog_schema_table(self):
        """Ensure the catalog, schema and table exist."""
        try:
            # Check if catalog exists
            try:
                self.w.catalogs.get(self.catalog)
            except Exception:
                logger.warning(f"Catalog {self.catalog} may not exist or not accessible")
                
            # Create schema if it doesn't exist
            try:
                self.w.schemas.get(f"{self.catalog}.{self.schema}")
            except Exception:
                try:
                    self.w.schemas.create(
                        name=self.schema,
                        catalog_name=self.catalog,
                        comment="UC-State schema for resource management"
                    )
                    logger.info(f"Created schema {self.catalog}.{self.schema}")
                except Exception as e:
                    logger.warning(f"Could not create schema: {e}")
            
            # Create table if it doesn't exist
            self._create_table_if_not_exists()
            
        except Exception as e:
            logger.error(f"Error ensuring catalog/schema/table: {e}")
            raise
    
    def _create_table_if_not_exists(self):
        """Create the state table if it doesn't exist."""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.full_table_name} (
            internal_id STRING NOT NULL,
            resource_type STRING NOT NULL,
            resource_data STRING NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (internal_id)
        ) USING DELTA
        TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
        """
        
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark.sql(create_table_sql)
                logger.info(f"Ensured table {self.full_table_name} exists")
            else:
                logger.warning("No active Spark session found, cannot create table")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise
    
    def add(self, resource_type: str, resource_obj: Any) -> str:
        """
        Add a resource to state.
        
        Args:
            resource_type: Type of resource (jobs, pipelines, apps, databaseinstances, models, catalogs)
            resource_obj: The API return object from Databricks SDK
            
        Returns:
            internal_id: Generated UUID for this resource
        """
        internal_id = str(uuid.uuid4())
        
        # Convert resource object to JSON string
        if hasattr(resource_obj, 'as_dict'):
            resource_data = json.dumps(resource_obj.as_dict())
        elif hasattr(resource_obj, '__dict__'):
            # Handle objects without as_dict() method
            resource_data = json.dumps(resource_obj.__dict__, default=str)
        else:
            # Handle primitive types or dictionaries
            resource_data = json.dumps(resource_obj, default=str)
        
        insert_sql = f"""
        INSERT INTO {self.full_table_name} 
        (internal_id, resource_type, resource_data, created_at)
        VALUES ('{internal_id}', '{resource_type}', '{resource_data}', CURRENT_TIMESTAMP())
        """
        
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark.sql(insert_sql)
                logger.info(f"Added {resource_type} resource with ID {internal_id}")
                return internal_id
            else:
                raise RuntimeError("No active Spark session found")
        except Exception as e:
            logger.error(f"Error adding resource: {e}")
            raise
    
    def list(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List resources in state.
        
        Args:
            resource_type: Filter by resource type (optional)
            
        Returns:
            List of state records
        """
        where_clause = f"WHERE resource_type = '{resource_type}'" if resource_type else ""
        query_sql = f"""
        SELECT internal_id, resource_type, resource_data, created_at 
        FROM {self.full_table_name} 
        {where_clause}
        ORDER BY created_at DESC
        """
        
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                df = spark.sql(query_sql)
                results = []
                for row in df.collect():
                    results.append({
                        'internal_id': row['internal_id'],
                        'resource_type': row['resource_type'],
                        'resource_data': json.loads(row['resource_data']),
                        'created_at': row['created_at']
                    })
                return results
            else:
                raise RuntimeError("No active Spark session found")
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            raise
    
    def remove(self, internal_id: str) -> bool:
        """
        Remove a resource from state by internal ID.
        
        Args:
            internal_id: The internal UUID of the resource
            
        Returns:
            True if removed, False if not found
        """
        delete_sql = f"""
        DELETE FROM {self.full_table_name} 
        WHERE internal_id = '{internal_id}'
        """
        
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                # Check if exists first
                exists_df = spark.sql(f"SELECT 1 FROM {self.full_table_name} WHERE internal_id = '{internal_id}'")
                if exists_df.count() == 0:
                    logger.warning(f"Resource with ID {internal_id} not found")
                    return False
                
                spark.sql(delete_sql)
                logger.info(f"Removed resource with ID {internal_id}")
                return True
            else:
                raise RuntimeError("No active Spark session found")
        except Exception as e:
            logger.error(f"Error removing resource: {e}")
            raise
    
    def clear_all(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """
        Remove all resources from Databricks and clear state.
        Deletion order: jobs → pipelines → models → apps → databaseinstances → catalogs
        
        Args:
            dry_run: If True, only show what would be deleted without actually deleting
            
        Returns:
            Dict with deletion results by resource type
        """
        # Define deletion order: jobs → pipelines → models → apps → databaseinstances → catalogs
        deletion_order = ['jobs', 'pipelines', 'models', 'apps', 'databaseinstances', 'catalogs']
        results = {}
        
        for resource_type in deletion_order:
            resources = self.list(resource_type)
            deleted_ids = []
            
            for resource in resources:
                resource_data = resource['resource_data']
                internal_id = resource['internal_id']
                
                if dry_run:
                    deleted_ids.append(f"Would delete {internal_id}")
                    continue
                
                try:
                    # Delete the actual resource from Databricks
                    if resource_type == 'jobs':
                        job_id = resource_data.get('job_id')
                        if job_id:
                            self.w.jobs.delete(job_id=int(job_id))
                            logger.info(f"Deleted job {job_id}")
                    
                    elif resource_type == 'pipelines':
                        pipeline_id = resource_data.get('pipeline_id')
                        if pipeline_id:
                            self.w.pipelines.delete(pipeline_id=pipeline_id)
                            logger.info(f"Deleted pipeline {pipeline_id}")
                    
                    elif resource_type == 'models':
                        # MLflow model endpoints
                        endpoint_name = resource_data.get('name')
                        if endpoint_name:
                            from mlflow.deployments import get_deploy_client
                            client = get_deploy_client("databricks")
                            client.delete_endpoint(endpoint=endpoint_name)
                            logger.info(f"Deleted model endpoint {endpoint_name}")
                    
                    elif resource_type == 'apps':
                        app_name = resource_data.get('name')
                        if app_name:
                            self.w.apps.delete(app_name)
                            logger.info(f"Deleted app {app_name}")
                    
                    elif resource_type == 'databaseinstances':
                        instance_name = resource_data.get('name')
                        if instance_name:
                            self.w.database.delete_database_instance(name=instance_name)
                            logger.info(f"Deleted database instance {instance_name}")
                    
                    elif resource_type == 'catalogs':
                        catalog_name = resource_data if isinstance(resource_data, str) else resource_data.get('name')
                        if catalog_name:
                            self.w.catalogs.delete(name=catalog_name, force=True)
                            logger.info(f"Deleted catalog {catalog_name}")
                    
                    # Remove from state
                    self.remove(internal_id)
                    deleted_ids.append(internal_id)
                    
                except Exception as e:
                    logger.error(f"Error deleting {resource_type} {internal_id}: {e}")
                    deleted_ids.append(f"ERROR: {internal_id} - {str(e)}")
            
            results[resource_type] = deleted_ids
        
        if not dry_run:
            # Clear any remaining state entries
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession()
                if spark:
                    spark.sql(f"DELETE FROM {self.full_table_name}")
                    logger.info("Cleared all remaining state entries")
            except Exception as e:
                logger.error(f"Error clearing remaining state: {e}")
        
        return results
    
    def get_resource_by_id(self, internal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific resource by internal ID.
        
        Args:
            internal_id: The internal UUID of the resource
            
        Returns:
            Resource record or None if not found
        """
        query_sql = f"""
        SELECT internal_id, resource_type, resource_data, created_at 
        FROM {self.full_table_name} 
        WHERE internal_id = '{internal_id}'
        """
        
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                df = spark.sql(query_sql)
                rows = df.collect()
                if rows:
                    row = rows[0]
                    return {
                        'internal_id': row['internal_id'],
                        'resource_type': row['resource_type'],
                        'resource_data': json.loads(row['resource_data']),
                        'created_at': row['created_at']
                    }
                return None
            else:
                raise RuntimeError("No active Spark session found")
        except Exception as e:
            logger.error(f"Error getting resource by ID: {e}")
            raise


# Convenience function for easy initialization
def create_state_manager(catalog: str, schema: str = "_caspers_state", table: str = "resources") -> UCState:
    """
    Create a UC-State manager instance.
    
    Args:
        catalog: The catalog name to store state in
        schema: Schema name (default: _caspers_state)
        table: Table name (default: resources)
        
    Returns:
        UCState instance
    """
    return UCState(catalog=catalog, schema=schema, table=table)
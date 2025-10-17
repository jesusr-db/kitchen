import { Utensils } from 'lucide-react';
import { LocationSelector } from '../common/LocationSelector';

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Utensils className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Casper's Kitchens
            </h1>
            <p className="text-sm text-gray-600">Digital Twin Operations Monitor</p>
          </div>
        </div>
        
        <LocationSelector />
      </div>
    </header>
  );
}

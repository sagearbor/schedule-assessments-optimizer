import React from 'react';
import { OptimizationSuggestion } from '../types';
import { 
  LightBulbIcon,
  ArrowsRightLeftIcon,
  TrashIcon,
  CalendarDaysIcon,
  WifiIcon
} from '@heroicons/react/24/outline';

interface SuggestionsListProps {
  suggestions: OptimizationSuggestion[];
}

const SuggestionsList: React.FC<SuggestionsListProps> = ({ suggestions }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'consolidation':
        return <ArrowsRightLeftIcon className="h-6 w-6" />;
      case 'elimination':
        return <TrashIcon className="h-6 w-6" />;
      case 'rescheduling':
        return <CalendarDaysIcon className="h-6 w-6" />;
      case 'remote_conversion':
        return <WifiIcon className="h-6 w-6" />;
      default:
        return <LightBulbIcon className="h-6 w-6" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'consolidation':
        return 'text-blue-600 bg-blue-50';
      case 'elimination':
        return 'text-red-600 bg-red-50';
      case 'rescheduling':
        return 'text-purple-600 bg-purple-50';
      case 'remote_conversion':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    const colors = {
      'Easy': 'bg-green-100 text-green-800',
      'Moderate': 'bg-yellow-100 text-yellow-800',
      'Hard': 'bg-red-100 text-red-800'
    };
    
    return colors[difficulty as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const sortedSuggestions = [...suggestions].sort((a, b) => 
    b.estimated_burden_reduction - a.estimated_burden_reduction
  );

  return (
    <div className="space-y-4">
      {sortedSuggestions.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <LightBulbIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No optimization suggestions available</p>
        </div>
      ) : (
        sortedSuggestions.map((suggestion, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start">
              <div className={`p-2 rounded-lg mr-4 ${getTypeColor(suggestion.type)}`}>
                {getIcon(suggestion.type)}
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {suggestion.description}
                  </h3>
                  <div className="flex items-center space-x-2 ml-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyBadge(suggestion.implementation_difficulty)}`}>
                      {suggestion.implementation_difficulty}
                    </span>
                    <span className="bg-primary-100 text-primary-800 px-3 py-1 text-sm rounded-full font-medium">
                      -{suggestion.estimated_burden_reduction.toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-3">{suggestion.impact}</p>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-700">
                    <strong>Affected visits:</strong> {suggestion.visits_affected.join(', ')}
                  </p>
                </div>
                
                {index < 5 && (
                  <div className="mt-3">
                    <span className="inline-flex items-center text-xs text-green-600 font-medium">
                      <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Applied in optimization
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default SuggestionsList;
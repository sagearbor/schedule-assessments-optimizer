import React from 'react';
import { Schedule, Visit } from '../types';
import { 
  CalendarIcon, 
  ClockIcon, 
  BeakerIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

interface ScheduleTableProps {
  schedule: Schedule;
  highlightChanges?: boolean;
}

const ScheduleTable: React.FC<ScheduleTableProps> = ({ schedule, highlightChanges = false }) => {
  const getVisitBadgeColor = (visit: Visit) => {
    if (visit.is_screening) return 'bg-purple-100 text-purple-800';
    if (visit.is_baseline) return 'bg-blue-100 text-blue-800';
    if (visit.is_treatment) return 'bg-green-100 text-green-800';
    if (visit.is_follow_up) return 'bg-gray-100 text-gray-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getVisitType = (visit: Visit) => {
    if (visit.is_screening) return 'Screening';
    if (visit.is_baseline) return 'Baseline';
    if (visit.is_treatment) return 'Treatment';
    if (visit.is_follow_up) return 'Follow-up';
    return 'Regular';
  };

  const calculateTotalDuration = (visit: Visit) => {
    return visit.assessments.reduce((sum, a) => sum + a.duration_minutes, 0);
  };

  const countInvasiveProcedures = (visit: Visit) => {
    return visit.assessments.filter(a => a.is_invasive).length;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Visit
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Day
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Window
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Assessments
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Duration
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Burden Indicators
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {schedule.visits.map((visit, index) => {
            const duration = calculateTotalDuration(visit);
            const invasiveCount = countInvasiveProcedures(visit);
            const hasFasting = visit.assessments.some(a => a.is_fasting_required);
            
            return (
              <tr key={visit.id || index} className={highlightChanges && visit.name.includes('(Combined)') ? 'bg-green-50' : ''}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {visit.name}
                    </div>
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full mt-1 ${getVisitBadgeColor(visit)}`}>
                      {getVisitType(visit)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center text-sm text-gray-900">
                    <CalendarIcon className="h-4 w-4 text-gray-400 mr-1" />
                    Day {visit.day}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {visit.window_days_before > 0 || visit.window_days_after > 0 ? (
                    <span>±{Math.max(visit.window_days_before, visit.window_days_after)} days</span>
                  ) : (
                    <span className="text-gray-400">Fixed</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">
                    <div className="flex items-center mb-1">
                      <BeakerIcon className="h-4 w-4 text-gray-400 mr-1" />
                      <span className="font-medium">{visit.assessments.length} assessments</span>
                    </div>
                    <div className="text-xs text-gray-500 max-w-xs">
                      {visit.assessments.slice(0, 3).map(a => a.name).join(', ')}
                      {visit.assessments.length > 3 && `, +${visit.assessments.length - 3} more`}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center text-sm text-gray-900">
                    <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                    {Math.round(duration / 60)}h {duration % 60}m
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {invasiveCount > 0 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                        <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                        {invasiveCount} invasive
                      </span>
                    )}
                    {hasFasting && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                        Fasting
                      </span>
                    )}
                    {duration > 240 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-orange-100 text-orange-800">
                        Long visit
                      </span>
                    )}
                    {visit.name.includes('(Remote)') && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        Remote option
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ScheduleTable;
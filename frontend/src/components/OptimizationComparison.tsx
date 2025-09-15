import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { OptimizationResult } from '../types';
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowDownIcon,
  ArrowUpIcon,
  MinusIcon
} from '@heroicons/react/24/outline';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface OptimizationComparisonProps {
  result: OptimizationResult;
}

const OptimizationComparison: React.FC<OptimizationComparisonProps> = ({ result }) => {
  // Calculate detailed metrics
  const originalVisitCount = result.original_schedule.visits.length;
  const optimizedVisitCount = result.optimized_schedule.visits.length;
  const visitReduction = originalVisitCount - optimizedVisitCount;

  // Calculate assessment changes per visit
  const assessmentChanges = result.original_schedule.visits.map((origVisit, idx) => {
    const optVisit = result.optimized_schedule.visits.find(v =>
      v.day === origVisit.day || v.name === origVisit.name
    );

    if (!optVisit) {
      return {
        visitName: origVisit.name,
        day: origVisit.day,
        originalCount: origVisit.assessments.length,
        optimizedCount: 0,
        removed: origVisit.assessments.length,
        status: 'removed'
      };
    }

    return {
      visitName: origVisit.name,
      day: origVisit.day,
      originalCount: origVisit.assessments.length,
      optimizedCount: optVisit.assessments.length,
      removed: origVisit.assessments.length - optVisit.assessments.length,
      status: origVisit.assessments.length > optVisit.assessments.length ? 'reduced' :
              origVisit.assessments.length === optVisit.assessments.length ? 'unchanged' : 'increased'
    };
  });

  // Prepare chart data
  const chartData = {
    labels: assessmentChanges.map(v => `${v.visitName} (Day ${v.day})`),
    datasets: [
      {
        label: 'Original Assessments',
        data: assessmentChanges.map(v => v.originalCount),
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
      },
      {
        label: 'Optimized Assessments',
        data: assessmentChanges.map(v => v.optimizedCount),
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 1,
      }
    ]
  };

  const chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Assessment Count by Visit - Before vs After Optimization',
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const idx = context.dataIndex;
            const change = assessmentChanges[idx];
            if (change.removed > 0) {
              return `Removed: ${change.removed} assessments`;
            } else if (change.removed < 0) {
              return `Added: ${Math.abs(change.removed)} assessments`;
            }
            return 'No change';
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Assessments'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Visits'
        }
      }
    }
  };

  // Calculate burden score improvements
  const patientBurdenImprovement =
    ((result.original_patient_burden.total_score - result.optimized_patient_burden.total_score) /
     result.original_patient_burden.total_score * 100).toFixed(1);

  const siteBurdenImprovement =
    ((result.original_site_burden.total_score - result.optimized_site_burden.total_score) /
     result.original_site_burden.total_score * 100).toFixed(1);

  // Count total assessments
  const originalTotalAssessments = result.original_schedule.visits.reduce(
    (sum, visit) => sum + visit.assessments.length, 0
  );
  const optimizedTotalAssessments = result.optimized_schedule.visits.reduce(
    (sum, visit) => sum + visit.assessments.length, 0
  );
  const assessmentReduction = originalTotalAssessments - optimizedTotalAssessments;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Visits</p>
              <p className="text-2xl font-bold text-gray-900">
                {originalVisitCount} → {optimizedVisitCount}
              </p>
            </div>
            {visitReduction > 0 ? (
              <ArrowDownIcon className="h-8 w-8 text-green-500" />
            ) : visitReduction < 0 ? (
              <ArrowUpIcon className="h-8 w-8 text-red-500" />
            ) : (
              <MinusIcon className="h-8 w-8 text-gray-400" />
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {visitReduction > 0 ? `${visitReduction} visits removed` :
             visitReduction < 0 ? `${Math.abs(visitReduction)} visits added` :
             'No change'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Assessments</p>
              <p className="text-2xl font-bold text-gray-900">
                {originalTotalAssessments} → {optimizedTotalAssessments}
              </p>
            </div>
            {assessmentReduction > 0 ? (
              <ArrowDownIcon className="h-8 w-8 text-green-500" />
            ) : assessmentReduction < 0 ? (
              <ArrowUpIcon className="h-8 w-8 text-red-500" />
            ) : (
              <MinusIcon className="h-8 w-8 text-gray-400" />
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {assessmentReduction > 0 ? `${assessmentReduction} assessments removed` :
             assessmentReduction < 0 ? `${Math.abs(assessmentReduction)} assessments added` :
             'No change'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Patient Burden</p>
              <p className="text-2xl font-bold text-gray-900">
                {patientBurdenImprovement}%
              </p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-sm text-gray-500 mt-2">Reduction</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Site Burden</p>
              <p className="text-2xl font-bold text-gray-900">
                {siteBurdenImprovement}%
              </p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-sm text-gray-500 mt-2">Reduction</p>
        </div>
      </div>

      {/* Detailed Comparison Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <Bar data={chartData} options={chartOptions} />
      </div>

      {/* Visit-by-Visit Changes */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Visit-by-Visit Changes</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {assessmentChanges.map((change, idx) => (
            <div key={idx} className="px-6 py-3 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  change.status === 'reduced' ? 'bg-green-500' :
                  change.status === 'removed' ? 'bg-red-500' :
                  change.status === 'increased' ? 'bg-yellow-500' :
                  'bg-gray-400'
                }`} />
                <div>
                  <p className="font-medium text-gray-900">{change.visitName}</p>
                  <p className="text-sm text-gray-500">Day {change.day}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {change.originalCount} → {change.optimizedCount} assessments
                  </p>
                  <p className={`text-xs ${
                    change.removed > 0 ? 'text-green-600' :
                    change.removed < 0 ? 'text-red-600' :
                    'text-gray-500'
                  }`}>
                    {change.removed > 0 ? `-${change.removed}` :
                     change.removed < 0 ? `+${Math.abs(change.removed)}` :
                     'No change'}
                  </p>
                </div>
                {change.status === 'reduced' && (
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                )}
                {change.status === 'removed' && (
                  <XCircleIcon className="h-5 w-5 text-red-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Applied Suggestions */}
      {result.suggestions && result.suggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Optimization Suggestions ({result.suggestions.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {result.suggestions.slice(0, 10).map((suggestion, idx) => (
              <div key={idx} className="px-6 py-3">
                <div className="flex items-start space-x-3">
                  <span className={`inline-flex items-center justify-center h-6 w-6 rounded-full text-xs font-medium ${
                    idx < 5 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {idx + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {suggestion.description}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Impact: {suggestion.impact} | Difficulty: {suggestion.implementation_difficulty}
                    </p>
                    {idx < 5 && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 mt-1">
                        Applied
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizationComparison;
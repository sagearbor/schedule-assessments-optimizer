import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ChartBarIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
  ArrowDownIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { OptimizationResult } from '../types';
import ScheduleTable from './ScheduleTable';
import BurdenChart from './BurdenChart';
import SuggestionsList from './SuggestionsList';
import OptimizationComparison from './OptimizationComparison';
import MCPConsensusDetails from './MCPConsensusDetails';

const OptimizationResults: React.FC = () => {
  const navigate = useNavigate();
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [activeTab, setActiveTab] = useState<'comparison' | 'suggestions' | 'warnings'>('comparison');

  useEffect(() => {
    const storedResult = sessionStorage.getItem('optimizationResult');
    if (storedResult) {
      setResult(JSON.parse(storedResult));
    } else {
      // Check if user has any saved results
      // For now, redirect to upload
      navigate('/upload');
    }
  }, [navigate]);

  if (!result) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  const patientBurdenReduction = Math.round(
    ((result.original_patient_burden.total_score - result.optimized_patient_burden.total_score) / 
    result.original_patient_burden.total_score) * 100
  );

  const siteBurdenReduction = Math.round(
    ((result.original_site_burden.total_score - result.optimized_site_burden.total_score) / 
    result.original_site_burden.total_score) * 100
  );

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with Summary */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Optimization Results
        </h1>
        
        {/* Success Banner */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <CheckCircleIcon className="h-6 w-6 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-900 mb-1">
                Optimization Complete
              </h3>
              <p className="text-green-700">
                {result.summary}
              </p>
            </div>
          </div>
        </div>

        {/* MCP Consensus Details */}
        <div className="mb-6">
          <MCPConsensusDetails consensusInfo={(result as any).mcp_consensus_info} />
        </div>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Patient Burden</span>
              <ArrowDownIcon className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {patientBurdenReduction}%
            </div>
            <div className="text-xs text-gray-500">
              {result.original_patient_burden.total_score.toFixed(1)} → {result.optimized_patient_burden.total_score.toFixed(1)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Site Burden</span>
              <ArrowDownIcon className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {siteBurdenReduction}%
            </div>
            <div className="text-xs text-gray-500">
              {result.original_site_burden.total_score.toFixed(1)} → {result.optimized_site_burden.total_score.toFixed(1)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Time Saved</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(result.original_patient_burden.patient_time_hours - result.optimized_patient_burden.patient_time_hours)}h
            </div>
            <div className="text-xs text-gray-500">Per patient</div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Visits Reduced</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {result.original_schedule.visits.length - result.optimized_schedule.visits.length}
            </div>
            <div className="text-xs text-gray-500">
              {result.original_schedule.visits.length} → {result.optimized_schedule.visits.length}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('comparison')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'comparison'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <ChartBarIcon className="h-5 w-5 mr-2" />
              Schedule Comparison
            </div>
          </button>
          <button
            onClick={() => setActiveTab('suggestions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'suggestions'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <LightBulbIcon className="h-5 w-5 mr-2" />
              Suggestions ({result.suggestions.length})
            </div>
          </button>
          <button
            onClick={() => setActiveTab('warnings')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'warnings'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
              Warnings ({result.warnings.length})
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'comparison' && (
        <div className="space-y-6">
          {/* Enhanced Optimization Comparison */}
          <OptimizationComparison result={result} />

          {/* Burden Comparison Charts */}
          <div className="grid md:grid-cols-2 gap-6">
            <BurdenChart
              title="Patient Burden Score"
              original={result.original_patient_burden}
              optimized={result.optimized_patient_burden}
              type="patient"
            />
            <BurdenChart
              title="Site Burden Score"
              original={result.original_site_burden}
              optimized={result.optimized_site_burden}
              type="site"
            />
          </div>

          {/* Schedule Tables */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Original Schedule
            </h3>
            <ScheduleTable schedule={result.original_schedule} />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Optimized Schedule
              <span className="ml-2 text-sm font-normal text-green-500">
                (Changes highlighted)
              </span>
            </h3>
            <ScheduleTable schedule={result.optimized_schedule} highlightChanges />
          </div>
        </div>
      )}

      {activeTab === 'suggestions' && (
        <SuggestionsList suggestions={result.suggestions} />
      )}

      {activeTab === 'warnings' && (
        <div className="space-y-4">
          {result.warnings.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-600">No compliance warnings detected</p>
            </div>
          ) : (
            result.warnings.map((warning, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start">
                  <ExclamationTriangleIcon 
                    className={`h-6 w-6 mr-3 flex-shrink-0 ${
                      warning.severity === 'High' || warning.severity === 'Critical' 
                        ? 'text-red-500' 
                        : warning.severity === 'Medium' 
                        ? 'text-yellow-500' 
                        : 'text-gray-400'
                    }`} 
                  />
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        warning.severity === 'High' || warning.severity === 'Critical' 
                          ? 'bg-red-100 text-red-800' 
                          : warning.severity === 'Medium' 
                          ? 'bg-yellow-100 text-yellow-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {warning.severity}
                      </span>
                      <span className="ml-2 text-sm text-gray-500">
                        {warning.type}
                      </span>
                    </div>
                    <p className="text-gray-900 mb-2">{warning.description}</p>
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>Affected visits:</strong> {warning.affected_visits.join(', ')}
                    </p>
                    <div className="bg-blue-50 rounded-lg p-3">
                      <p className="text-sm text-blue-900">
                        <strong>Recommendation:</strong> {warning.recommendation}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={() => navigate('/upload')}
          className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          Optimize Another Schedule
        </button>
        <button
          onClick={() => window.print()}
          className="bg-primary-600 text-white px-6 py-3 rounded-md font-medium hover:bg-primary-700 transition-colors"
        >
          Export Report
        </button>
      </div>
    </div>
  );
};

export default OptimizationResults;
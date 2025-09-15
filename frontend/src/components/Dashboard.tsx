import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { 
  ChartBarIcon, 
  DocumentArrowUpIcon, 
  BeakerIcon,
  LightBulbIcon,
  ClockIcon,
  UsersIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import { scheduleService } from '../services/api';
import { Schedule } from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const loadDemoData = async (type: string) => {
    setIsLoading(true);
    try {
      let schedule: Schedule;
      
      if (type === 'complex') {
        schedule = await scheduleService.getComplexDemoData();
      } else {
        const therapeuticArea = type;
        schedule = await scheduleService.getDemoData({ 
          therapeutic_area: therapeuticArea,
          phase: therapeuticArea === 'cardiology' ? '3' : '2'
        });
      }
      
      // Store in session storage for the upload page to use
      sessionStorage.setItem('demoSchedule', JSON.stringify(schedule));
      toast.success(`Loaded ${type} demo data`);
      navigate('/upload');
    } catch (error: any) {
      console.error('Demo data error:', error);
      toast.error(error.response?.data?.detail || 'Failed to load demo data. Please check if the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadDemoData = async (type: string) => {
    setIsLoading(true);
    try {
      let schedule: Schedule;
      
      if (type === 'complex') {
        schedule = await scheduleService.getComplexDemoData();
      } else {
        const therapeuticArea = type;
        schedule = await scheduleService.getDemoData({ 
          therapeutic_area: therapeuticArea,
          phase: therapeuticArea === 'cardiology' ? '3' : '2'
        });
      }
      
      // Create and download JSON file
      const dataStr = JSON.stringify(schedule, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `demo-${type}-schedule.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${type} demo data`);
    } catch (error: any) {
      console.error('Demo data download error:', error);
      toast.error(error.response?.data?.detail || 'Failed to download demo data');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Optimize Your Clinical Trial Schedule
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Reduce patient burden and site complexity while maintaining scientific integrity. 
          Our AI-powered optimizer analyzes your Schedule of Assessments and provides 
          actionable recommendations.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <DocumentArrowUpIcon className="h-8 w-8 text-primary-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">Upload Your Schedule</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Upload your existing Schedule of Assessments in CSV or JSON format for analysis.
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="bg-primary-600 text-white px-6 py-3 rounded-md font-medium hover:bg-primary-700 transition-colors"
          >
            Upload Schedule
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <BeakerIcon className="h-8 w-8 text-success-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">Try Demo Data</h2>
          </div>
          <p className="text-gray-600 mb-2">
            Explore the optimizer with realistic clinical trial schedules from different therapeutic areas.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Click to load demo data directly, or use the download button to save as JSON for testing upload.
          </p>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadDemoData('oncology')}
                disabled={isLoading}
                className="bg-success-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-success-700 transition-colors disabled:opacity-50 flex-1"
                title="Load oncology demo data"
              >
                {isLoading ? 'Loading...' : 'Oncology Trial'}
              </button>
              <button
                onClick={() => downloadDemoData('oncology')}
                disabled={isLoading}
                className="bg-gray-600 text-white p-2 rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                title="Download oncology demo data as JSON"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadDemoData('cardiology')}
                disabled={isLoading}
                className="bg-success-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-success-700 transition-colors disabled:opacity-50 flex-1"
                title="Load cardiology demo data"
              >
                {isLoading ? 'Loading...' : 'Cardiology Trial'}
              </button>
              <button
                onClick={() => downloadDemoData('cardiology')}
                disabled={isLoading}
                className="bg-gray-600 text-white p-2 rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                title="Download cardiology demo data as JSON"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadDemoData('neurology')}
                disabled={isLoading}
                className="bg-success-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-success-700 transition-colors disabled:opacity-50 flex-1"
                title="Load neurology demo data"
              >
                {isLoading ? 'Loading...' : 'Neurology Trial'}
              </button>
              <button
                onClick={() => downloadDemoData('neurology')}
                disabled={isLoading}
                className="bg-gray-600 text-white p-2 rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                title="Download neurology demo data as JSON"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadDemoData('complex')}
                disabled={isLoading}
                className="bg-warning-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-warning-700 transition-colors disabled:opacity-50 flex-1"
                title="Load complex unoptimized demo data"
              >
                {isLoading ? 'Loading...' : 'Complex (Unoptimized)'}
              </button>
              <button
                onClick={() => downloadDemoData('complex')}
                disabled={isLoading}
                className="bg-gray-600 text-white p-2 rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                title="Download complex demo data as JSON"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <ChartBarIcon className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Burden Analysis
            </h3>
            <p className="text-gray-600">
              Calculates comprehensive burden scores for both patients and sites, 
              considering time, travel, invasiveness, and complexity.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <LightBulbIcon className="h-12 w-12 text-warning-600 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Smart Optimization
            </h3>
            <p className="text-gray-600">
              AI-powered rules engine identifies redundancies, suggests visit 
              consolidations, and recommends remote alternatives.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <UsersIcon className="h-12 w-12 text-success-600 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Compliance Check
            </h3>
            <p className="text-gray-600">
              Ensures optimizations maintain regulatory compliance and scientific 
              validity while improving feasibility.
            </p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Typical Optimization Results
        </h2>
        <div className="grid md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold mb-1">25%</div>
            <div className="text-primary-100">Burden Reduction</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-1">3-5</div>
            <div className="text-primary-100">Visits Consolidated</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-1">15%</div>
            <div className="text-primary-100">Cost Savings</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-1">20%</div>
            <div className="text-primary-100">Better Retention</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
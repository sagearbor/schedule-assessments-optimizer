import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import { 
  CloudArrowUpIcon, 
  DocumentTextIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';
import { scheduleService } from '../services/api';
import { Schedule } from '../types';
import ScheduleTable from './ScheduleTable';

const ScheduleUpload: React.FC = () => {
  const navigate = useNavigate();
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  useEffect(() => {
    // Check if there's demo data in session storage
    const demoData = sessionStorage.getItem('demoSchedule');
    if (demoData) {
      setSchedule(JSON.parse(demoData));
      sessionStorage.removeItem('demoSchedule');
    }
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    setUploadedFile(file);
    
    try {
      const uploadedSchedule = await scheduleService.uploadSchedule(file);
      setSchedule(uploadedSchedule);
      toast.success('Schedule uploaded successfully');
    } catch (error) {
      toast.error('Failed to parse schedule file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleOptimize = async () => {
    if (!schedule) return;
    
    setIsOptimizing(true);
    try {
      const result = await scheduleService.optimizeSchedule(schedule);
      // Store result in session storage for the results page
      sessionStorage.setItem('optimizationResult', JSON.stringify(result));
      toast.success('Optimization complete!');
      navigate('/results');
    } catch (error) {
      toast.error('Optimization failed. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  };

  const clearSchedule = () => {
    setSchedule(null);
    setUploadedFile(null);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Schedule of Assessments
        </h1>
        <p className="text-gray-600">
          Upload your clinical trial schedule for optimization analysis
        </p>
      </div>

      {!schedule ? (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive
                ? 'Drop the file here'
                : 'Drag & drop your schedule file here'}
            </p>
            <p className="text-sm text-gray-600 mb-4">
              or click to browse
            </p>
            <p className="text-xs text-gray-500">
              Supported formats: CSV, JSON
            </p>
          </div>

          <div className="mt-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              File Format Guidelines
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <DocumentTextIcon className="h-5 w-5 text-primary-600 mr-2" />
                  <span className="font-medium text-gray-900">JSON Format</span>
                </div>
                <p className="text-sm text-gray-600">
                  Include protocol details, visits array with assessments, and total duration.
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <DocumentTextIcon className="h-5 w-5 text-success-600 mr-2" />
                  <span className="font-medium text-gray-900">CSV Format</span>
                </div>
                <p className="text-sm text-gray-600">
                  Columns for visit name, day, assessments, duration, and other attributes.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {schedule.protocol_name}
                </h2>
                <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
                  <span>Phase {schedule.phase}</span>
                  <span>{schedule.therapeutic_area}</span>
                  <span>{schedule.total_duration_days} days</span>
                  <span>{schedule.visits.length} visits</span>
                </div>
              </div>
              <button
                onClick={clearSchedule}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {uploadedFile && (
              <div className="bg-gray-50 rounded-lg px-4 py-2 mb-4 inline-block">
                <span className="text-sm text-gray-600">
                  Uploaded: {uploadedFile.name}
                </span>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Schedule Overview
            </h3>
            <ScheduleTable schedule={schedule} />
          </div>

          <div className="flex justify-between">
            <button
              onClick={clearSchedule}
              className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Upload Different Schedule
            </button>
            <button
              onClick={handleOptimize}
              disabled={isOptimizing}
              className="bg-primary-600 text-white px-8 py-3 rounded-md font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isOptimizing ? 'Optimizing...' : 'Optimize Schedule'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ScheduleUpload;
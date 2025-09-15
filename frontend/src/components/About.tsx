import React, { useState, useEffect } from 'react';
import { InformationCircleIcon, ChartBarIcon, BeakerIcon } from '@heroicons/react/24/outline';

const About: React.FC = () => {
  const [showSimple, setShowSimple] = useState(true);
  const [showDetailed, setShowDetailed] = useState(false);
  const [simpleFlowContent, setSimpleFlowContent] = useState('');
  const [detailedFlowContent, setDetailedFlowContent] = useState('');

  useEffect(() => {
    // Load diagram files
    fetch('/diagrams/data-flow-simple.mmd')
      .then(res => res.text())
      .then(data => setSimpleFlowContent(data))
      .catch(() => setSimpleFlowContent('graph TD\n    A[User] -->|Upload Schedule| B[Frontend UI]\n    B -->|Submit for Optimization| C[Backend API]\n    C -->|Apply Rules| D[Rules Engine]\n    D -->|Calculate Burden| E[Burden Calculator]\n    E -->|Return Results| C\n    C -->|Optimized Schedule| B\n    B -->|Display Results| A'));

    fetch('/diagrams/data-flow-detailed.mmd')
      .then(res => res.text())
      .then(data => setDetailedFlowContent(data))
      .catch(() => setDetailedFlowContent('graph TB\n    A[User] -->|Upload| B[Frontend]\n    B -->|API Call| C[Backend]\n    C -->|Process| D[Engine]\n    D -->|Results| A'));
  }, []);

  useEffect(() => {
    // Dynamically load mermaid
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
    script.async = true;
    script.onload = () => {
      (window as any).mermaid?.initialize({ 
        startOnLoad: true,
        theme: 'default',
        themeVariables: {
          primaryColor: '#6366f1',
          primaryTextColor: '#fff',
          primaryBorderColor: '#4f46e5',
          lineColor: '#e5e7eb',
          secondaryColor: '#f3f4f6',
          tertiaryColor: '#fef3c7'
        }
      });
      (window as any).mermaid?.contentLoaded();
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  useEffect(() => {
    // Re-render mermaid diagrams when visibility changes
    if ((window as any).mermaid) {
      (window as any).mermaid.contentLoaded();
    }
  }, [showSimple, showDetailed]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center mb-4">
            <InformationCircleIcon className="h-8 w-8 text-indigo-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">About SoA Optimizer</h1>
          </div>
          
          <div className="prose max-w-none text-gray-600">
            <p className="text-lg mb-4">
              The Schedule of Assessments (SoA) Optimizer is an intelligent tool designed to streamline 
              clinical trial protocols by analyzing and optimizing assessment schedules for reduced patient 
              and site burden while maintaining trial integrity..
            </p>
          </div>
        </div>

        {/* Key Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center mb-3">
              <ChartBarIcon className="h-6 w-6 text-indigo-600 mr-2" />
              <h3 className="text-lg font-semibold">Burden Analysis</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Calculates comprehensive burden scores for both patients and sites, considering time, 
              travel, invasiveness, staff requirements, and resource utilization.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center mb-3">
              <BeakerIcon className="h-6 w-6 text-indigo-600 mr-2" />
              <h3 className="text-lg font-semibold">Smart Optimization</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Applies intelligent rules to detect redundancies, consolidate visits, and ensure 
              logistical feasibility while maintaining scientific validity.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center mb-3">
              <InformationCircleIcon className="h-6 w-6 text-indigo-600 mr-2" />
              <h3 className="text-lg font-semibold">MCP Integration</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Integrates with{' '}
              <span className="relative inline-block group cursor-help">
                <span className="font-medium text-indigo-600 border-b border-dotted border-indigo-400">
                  Protocol Complexity Analyzer
                </span>
                <div className="absolute z-50 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity duration-200 bg-gray-900 text-white text-xs rounded-lg p-3 mt-1 w-64 left-1/2 transform -translate-x-1/2">
                  <div className="font-semibold mb-1">Protocol Complexity Analyzer</div>
                  <p>Analyzes clinical trial protocols to calculate complexity scores based on:</p>
                  <ul className="mt-1 space-y-0.5">
                    <li>• Number and frequency of visits</li>
                    <li>• Assessment types and procedures</li>
                    <li>• Patient population requirements</li>
                    <li>• Overall protocol burden metrics</li>
                  </ul>
                  <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
                </div>
              </span>
              {' '}and{' '}
              <span className="relative inline-block group cursor-help">
                <span className="font-medium text-indigo-600 border-b border-dotted border-indigo-400">
                  Compliance Knowledge Base
                </span>
                <div className="absolute z-50 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity duration-200 bg-gray-900 text-white text-xs rounded-lg p-3 mt-1 w-64 left-1/2 transform -translate-x-1/2">
                  <div className="font-semibold mb-1">Compliance Knowledge Base</div>
                  <p>Provides regulatory compliance insights including:</p>
                  <ul className="mt-1 space-y-0.5">
                    <li>• FDA and EMA guideline compliance</li>
                    <li>• Historical trial performance data</li>
                    <li>• Best practices for patient retention</li>
                    <li>• Risk assessment for protocol deviations</li>
                  </ul>
                  <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
                </div>
              </span>
              {' '}services for comprehensive protocol analysis.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
          
          <div className="space-y-4 mb-6">
            <div className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-semibold text-sm">1</span>
              <div className="ml-3">
                <h4 className="font-semibold text-gray-900">Upload Your Schedule</h4>
                <p className="text-gray-600 text-sm">Import your Schedule of Assessments via Excel, CSV, or manual entry</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-semibold text-sm">2</span>
              <div className="ml-3">
                <h4 className="font-semibold text-gray-900">Automated Analysis</h4>
                <p className="text-gray-600 text-sm">The system analyzes your protocol using advanced rules and burden calculations</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-semibold text-sm">3</span>
              <div className="ml-3">
                <h4 className="font-semibold text-gray-900">Review Recommendations</h4>
                <p className="text-gray-600 text-sm">Get actionable suggestions to reduce burden while maintaining trial integrity</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <span className="flex-shrink-0 w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-semibold text-sm">4</span>
              <div className="ml-3">
                <h4 className="font-semibold text-gray-900">Export Optimized Schedule</h4>
                <p className="text-gray-600 text-sm">Download your optimized schedule with detailed burden reports</p>
              </div>
            </div>
          </div>
        </div>

        {/* Data Flow Diagrams */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">System Architecture & Data Flow</h2>
          
          {/* Toggle Buttons */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setShowSimple(!showSimple)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                showSimple 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {showSimple ? 'Hide' : 'Show'} Simple Flow
            </button>
            <button
              onClick={() => setShowDetailed(!showDetailed)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                showDetailed 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {showDetailed ? 'Hide' : 'Show'} Detailed Flow
            </button>
          </div>

          {/* Simple Flow Diagram */}
          {showSimple && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Simplified Data Flow</h3>
              <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <div className="mermaid">
                  {simpleFlowContent}
                </div>
              </div>
            </div>
          )}

          {/* Detailed Flow Diagram */}
          {showDetailed && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Detailed System Architecture</h3>
              <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <div className="mermaid">
                  {detailedFlowContent}
                </div>
              </div>
            </div>
          )}

          {!showSimple && !showDetailed && (
            <p className="text-gray-500 text-center py-8">
              Click a button above to view the data flow diagrams
            </p>
          )}
        </div>

        {/* Technical Stack */}
        <div className="bg-white rounded-lg shadow-sm p-6 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Technical Stack</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Backend</h3>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• FastAPI (Python) - High-performance API framework</li>
                <li>• SQLAlchemy - Database ORM</li>
                <li>• Pydantic - Data validation</li>
                <li>• JWT Authentication - Secure user sessions</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Frontend</h3>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• React with TypeScript - Type-safe UI development</li>
                <li>• Tailwind CSS - Modern styling</li>
                <li>• Chart.js - Data visualization</li>
                <li>• React Router - Client-side routing</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
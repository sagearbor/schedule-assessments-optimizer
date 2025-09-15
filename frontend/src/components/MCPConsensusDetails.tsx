import React, { useState } from 'react';
import {
  QuestionMarkCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

interface MCPConsensusInfo {
  method: string;
  confidence: number;
  details: string;
  pattern_confidence?: number;
  llm_confidence?: number;
  arbitration_used?: boolean;
}

interface MCPConsensusDetailsProps {
  consensusInfo?: MCPConsensusInfo;
}

const MCPConsensusDetails: React.FC<MCPConsensusDetailsProps> = ({ consensusInfo }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!consensusInfo) {
    return null;
  }

  const getMethodIcon = () => {
    if (consensusInfo.arbitration_used) {
      return (
        <div className="relative group">
          <ExclamationCircleIcon
            className="h-5 w-5 text-yellow-500 cursor-help"
            title="LLM Arbitration was required due to disagreement between pattern matching and LLM validation"
          />
          <div className="absolute z-10 invisible group-hover:visible bg-gray-800 text-white text-xs rounded-lg p-2 w-64 -top-2 left-6">
            <p className="font-semibold mb-1">LLM Arbitration Details</p>
            <p>Pattern confidence: {consensusInfo.pattern_confidence}%</p>
            <p>LLM confidence: {consensusInfo.llm_confidence}%</p>
            <p>Difference: {Math.abs((consensusInfo.pattern_confidence || 0) - (consensusInfo.llm_confidence || 0))}%</p>
            <p className="mt-1 text-yellow-300">GPT-5 mini was used to resolve the disagreement</p>
          </div>
        </div>
      );
    }
    if (consensusInfo.confidence >= 80) {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    }
    return <CpuChipIcon className="h-5 w-5 text-gray-400" />;
  };

  const getMethodLabel = () => {
    if (consensusInfo.method === 'not_available') {
      return 'MCP Analysis Not Available';
    }
    if (consensusInfo.arbitration_used) {
      return 'LLM Arbitration Used';
    }
    if (consensusInfo.pattern_confidence && consensusInfo.llm_confidence) {
      const diff = Math.abs(consensusInfo.pattern_confidence - consensusInfo.llm_confidence);
      if (diff <= 20) {
        return 'Pattern & LLM Agreement';
      }
    }
    if (consensusInfo.pattern_confidence && !consensusInfo.llm_confidence) {
      return 'Pattern Matching Only';
    }
    return 'MCP Analysis Completed';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 85) return 'text-green-500';
    if (confidence >= 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between hover:bg-gray-100 rounded-md p-2 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <QuestionMarkCircleIcon className="h-5 w-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">MCP Consensus Details</span>
          {getMethodIcon()}
        </div>
        {isExpanded ? (
          <ChevronUpIcon className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDownIcon className="h-4 w-4 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-3 p-3 bg-white rounded-md space-y-3">
          {/* Analysis Method */}
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-600 uppercase">Analysis Method</span>
              <span className="text-sm font-medium text-gray-900">{getMethodLabel()}</span>
            </div>
          </div>

          {/* Overall Confidence */}
          {consensusInfo.confidence > 0 && (
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-600 uppercase">Overall Confidence</span>
                <span className={`text-sm font-bold ${getConfidenceColor(consensusInfo.confidence)}`}>
                  {consensusInfo.confidence}%
                </span>
              </div>
              <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    consensusInfo.confidence >= 85 ? 'bg-green-500' :
                    consensusInfo.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${consensusInfo.confidence}%` }}
                />
              </div>
            </div>
          )}

          {/* Pattern Matching Confidence */}
          {consensusInfo.pattern_confidence !== undefined && consensusInfo.pattern_confidence > 0 && (
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Pattern Matching</span>
                <span className={`text-sm ${getConfidenceColor(consensusInfo.pattern_confidence)}`}>
                  {consensusInfo.pattern_confidence}%
                </span>
              </div>
              <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                <div
                  className={`h-1 rounded-full ${
                    consensusInfo.pattern_confidence >= 85 ? 'bg-green-500' :
                    consensusInfo.pattern_confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${consensusInfo.pattern_confidence}%` }}
                />
              </div>
            </div>
          )}

          {/* LLM Confidence */}
          {consensusInfo.llm_confidence !== undefined && consensusInfo.llm_confidence > 0 && (
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">LLM Validation</span>
                <span className={`text-sm ${getConfidenceColor(consensusInfo.llm_confidence)}`}>
                  {consensusInfo.llm_confidence}%
                </span>
              </div>
              <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                <div
                  className={`h-1 rounded-full ${
                    consensusInfo.llm_confidence >= 85 ? 'bg-green-500' :
                    consensusInfo.llm_confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${consensusInfo.llm_confidence}%` }}
                />
              </div>
            </div>
          )}

          {/* Arbitration Status */}
          {consensusInfo.arbitration_used && (
            <div className="bg-yellow-50 p-2 rounded-md border border-yellow-200">
              <div className="flex items-center space-x-2">
                <ExclamationCircleIcon className="h-4 w-4 text-yellow-500" />
                <div className="flex-1">
                  <span className="text-xs text-yellow-800 font-medium">
                    Arbitration Required
                  </span>
                  <p className="text-xs text-yellow-700 mt-0.5">
                    Pattern ({consensusInfo.pattern_confidence}%) and LLM ({consensusInfo.llm_confidence}%)
                    disagreed by {Math.abs((consensusInfo.pattern_confidence || 0) - (consensusInfo.llm_confidence || 0))}%
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Details */}
          {consensusInfo.details && (
            <div className="pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-600">{consensusInfo.details}</p>
            </div>
          )}

          {/* Legend */}
          <div className="pt-2 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Confidence Levels</p>
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>High Confidence (≥85%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span>Medium Confidence (70-84%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span>Low Confidence (&lt;70%)</span>
              </div>
              <div className="flex items-center space-x-2 mt-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                <span>Not Available / No Data</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MCPConsensusDetails;
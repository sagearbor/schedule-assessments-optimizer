import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { BurdenScore, SiteBurdenScore } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BurdenChartProps {
  title: string;
  original: BurdenScore | SiteBurdenScore;
  optimized: BurdenScore | SiteBurdenScore;
  type: 'patient' | 'site';
}

const BurdenChart: React.FC<BurdenChartProps> = ({ title, original, optimized, type }) => {
  const getChartData = () => {
    if (type === 'patient') {
      const orig = original as BurdenScore;
      const opt = optimized as BurdenScore;
      
      return {
        labels: ['Time (hrs)', 'Visits', 'Invasive', 'Fasting', 'Discomfort', 'Total Score'],
        datasets: [
          {
            label: 'Original',
            data: [
              orig.patient_time_hours,
              orig.patient_travel_count,
              orig.invasive_procedures_count,
              orig.fasting_requirements_count,
              orig.average_discomfort_level * 10, // Scale for visibility
              orig.total_score
            ],
            backgroundColor: 'rgba(239, 68, 68, 0.5)',
            borderColor: 'rgba(239, 68, 68, 1)',
            borderWidth: 1
          },
          {
            label: 'Optimized',
            data: [
              opt.patient_time_hours,
              opt.patient_travel_count,
              opt.invasive_procedures_count,
              opt.fasting_requirements_count,
              opt.average_discomfort_level * 10,
              opt.total_score
            ],
            backgroundColor: 'rgba(34, 197, 94, 0.5)',
            borderColor: 'rgba(34, 197, 94, 1)',
            borderWidth: 1
          }
        ]
      };
    } else {
      const orig = original as SiteBurdenScore;
      const opt = optimized as SiteBurdenScore;
      
      return {
        labels: ['Staff Hours', 'Equipment', 'Staff Roles', 'Cost ($k)', 'Complex', 'Total Score'],
        datasets: [
          {
            label: 'Original',
            data: [
              orig.total_staff_hours,
              orig.unique_equipment_count,
              orig.unique_staff_roles_count,
              orig.total_cost / 1000, // Convert to thousands
              orig.complex_procedures_count,
              orig.total_score
            ],
            backgroundColor: 'rgba(239, 68, 68, 0.5)',
            borderColor: 'rgba(239, 68, 68, 1)',
            borderWidth: 1
          },
          {
            label: 'Optimized',
            data: [
              opt.total_staff_hours,
              opt.unique_equipment_count,
              opt.unique_staff_roles_count,
              opt.total_cost / 1000,
              opt.complex_procedures_count,
              opt.total_score
            ],
            backgroundColor: 'rgba(34, 197, 94, 0.5)',
            borderColor: 'rgba(34, 197, 94, 1)',
            borderWidth: 1
          }
        ]
      };
    }
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toFixed(1);
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  const getCategoryBadge = (category: string) => {
    const colors = {
      'Low': 'bg-green-100 text-green-800',
      'Moderate': 'bg-yellow-100 text-yellow-800',
      'High': 'bg-orange-100 text-orange-800',
      'Very High': 'bg-red-100 text-red-800'
    };
    
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <Bar options={options} data={getChartData()} />
      </div>
      
      <div className="flex justify-between items-center border-t pt-4">
        <div className="text-center">
          <p className="text-sm text-gray-500">Original</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getCategoryBadge(original.category)}`}>
            {original.category}
          </span>
        </div>
        
        <div className="text-center">
          <p className="text-sm text-gray-500">Optimized</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getCategoryBadge(optimized.category)}`}>
            {optimized.category}
          </span>
        </div>
      </div>
    </div>
  );
};

export default BurdenChart;
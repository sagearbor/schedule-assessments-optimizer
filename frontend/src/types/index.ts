export interface Assessment {
  id?: string;
  name: string;
  type: string;
  duration_minutes: number;
  is_invasive: boolean;
  is_fasting_required: boolean;
  equipment_needed: string[];
  staff_required: string[];
  cost_estimate: number;
  patient_discomfort_level: number;
  can_be_done_remotely: boolean;
}

export interface Visit {
  id?: string;
  name: string;
  day: number;
  window_days_before: number;
  window_days_after: number;
  assessments: Assessment[];
  is_screening?: boolean;
  is_baseline?: boolean;
  is_treatment?: boolean;
  is_follow_up?: boolean;
  notes?: string;
}

export interface Schedule {
  id?: string;
  protocol_name: string;
  protocol_version: string;
  therapeutic_area: string;
  phase: string;
  visits: Visit[];
  total_duration_days: number;
  created_at?: string;
  updated_at?: string;
}

export interface BurdenScore {
  patient_time_hours: number;
  patient_travel_count: number;
  invasive_procedures_count: number;
  fasting_requirements_count: number;
  average_discomfort_level: number;
  total_score: number;
  category: string;
}

export interface SiteBurdenScore {
  total_staff_hours: number;
  unique_equipment_count: number;
  unique_staff_roles_count: number;
  total_cost: number;
  complex_procedures_count: number;
  total_score: number;
  category: string;
}

export interface OptimizationSuggestion {
  type: string;
  description: string;
  impact: string;
  visits_affected: string[];
  estimated_burden_reduction: number;
  implementation_difficulty: string;
}

export interface ComplianceWarning {
  severity: string;
  type: string;
  description: string;
  affected_visits: string[];
  recommendation: string;
}

export interface OptimizationResult {
  original_schedule: Schedule;
  optimized_schedule: Schedule;
  original_patient_burden: BurdenScore;
  optimized_patient_burden: BurdenScore;
  original_site_burden: SiteBurdenScore;
  optimized_site_burden: SiteBurdenScore;
  suggestions: OptimizationSuggestion[];
  warnings: ComplianceWarning[];
  improvement_percentage: number;
  summary: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  organization?: string;
  role: string;
  created_at?: string;
  is_active: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface DemoDataRequest {
  therapeutic_area?: string;
  phase?: string;
  complexity?: string;
}
/**
 * React Hook for Wizard Lifecycle Protection
 *
 * Provides real-time protection status for wizards based on their usage state:
 * - Draft: Never run, full editing allowed
 * - In-Use: Has runs but none stored, edits allowed with warning
 * - Published: Has stored runs, read-only (clone/version alternatives)
 */
import { useQuery } from '@tanstack/react-query';
import { wizardService } from '../services/wizard.service';

export interface WizardProtectionStatus {
  state: 'draft' | 'in_use' | 'published';
  can_edit: boolean;
  can_delete: boolean;
  total_runs: number;
  stored_runs: number;
  in_progress_runs: number;
  completed_runs: number;
  message: string;
  actions: string[];
}

export const useWizardProtection = (wizardId: string | undefined) => {
  return useQuery<WizardProtectionStatus>({
    queryKey: ['wizard-protection', wizardId],
    queryFn: () => wizardService.getProtectionStatus(wizardId!),
    enabled: !!wizardId,
    staleTime: 10000, // Cache for 10 seconds
    refetchOnWindowFocus: true, // Refresh when user returns to tab
  });
};

/**
 * Helper function to get badge color for lifecycle state
 */
export const getStateColor = (state: 'draft' | 'in_use' | 'published') => {
  switch (state) {
    case 'draft':
      return 'success'; // Green
    case 'in_use':
      return 'warning'; // Orange
    case 'published':
      return 'error'; // Red
    default:
      return 'default';
  }
};

/**
 * Helper function to get state label
 */
export const getStateLabel = (state: 'draft' | 'in_use' | 'published') => {
  switch (state) {
    case 'draft':
      return 'Draft';
    case 'in_use':
      return 'In Use';
    case 'published':
      return 'Published';
    default:
      return 'Unknown';
  }
};

/**
 * Helper function to get state icon
 */
export const getStateIcon = (state: 'draft' | 'in_use' | 'published') => {
  switch (state) {
    case 'draft':
      return 'edit'; // EditIcon
    case 'in_use':
      return 'warning'; // WarningIcon
    case 'published':
      return 'lock'; // LockIcon
    default:
      return 'help';
  }
};

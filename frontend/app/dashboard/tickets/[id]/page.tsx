'use client';

import React, { useEffect, useState } from 'react';
import { ticketsApi } from '@/lib/tickets';
import { canApproveTickets } from '@/lib/auth';
import { TicketResponse } from '@/types/api';
import { Badge, BadgeColor } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import Link from 'next/link';

export default function TicketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [ticket, setTicket] = useState<TicketResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isStaff, setIsStaff] = useState(false);
  const [confirmAction, setConfirmAction] = useState<'approve' | 'reject' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const unwrappedParams = React.use(params);
  const ticketId = unwrappedParams.id;

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const data = await ticketsApi.getById(ticketId);
        setTicket(data);
        setIsStaff(canApproveTickets());
      } catch (err: unknown) {
        setError('Unable to load ticket details. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTicket();
  }, [ticketId]);

  const getStatusColor = (status: string): BadgeColor => {
    switch (status.toUpperCase()) {
      case 'OPEN': return 'blue';
      case 'IN_PROGRESS': return 'yellow';
      case 'PENDING_APPROVAL': return 'purple';
      case 'APPROVED': return 'green';
      case 'RESOLVED': return 'green';
      case 'REJECTED': return 'red';
      case 'CLOSED': return 'gray';
      default: return 'gray';
    }
  };

  const formatStatus = (status: string): string => {
    switch (status.toUpperCase()) {
      case 'PENDING_APPROVAL': return 'Pending Approval';
      case 'IN_PROGRESS': return 'In Progress';
      case 'OPEN': return 'Open';
      case 'APPROVED': return 'Approved';
      case 'REJECTED': return 'Rejected';
      case 'RESOLVED': return 'Resolved';
      case 'CLOSED': return 'Closed';
      default: return status;
    }
  };

  const getPriorityColor = (priority: string): BadgeColor => {
    switch (priority.toUpperCase()) {
      case 'HIGH': return 'red';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'blue';
      default: return 'gray';
    }
  };

  const handleDecision = async (decision: 'approve' | 'reject') => {
    if (!ticket || isSubmitting) return;
    setIsSubmitting(true);
    setActionFeedback(null);

    try {
      let updatedTicket: TicketResponse;
      if (decision === 'approve') {
        updatedTicket = await ticketsApi.approve(ticket.id);
        setActionFeedback({
          type: 'success',
          message: `Ticket #${ticket.id} was successfully approved.`,
        });
      } else {
        updatedTicket = await ticketsApi.reject(ticket.id);
        setActionFeedback({
          type: 'success',
          message: `Ticket #${ticket.id} was successfully rejected.`,
        });
      }
      setTicket(updatedTicket);
      setConfirmAction(null);
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } }; message?: string };
      const detailMsg = errorObj.response?.data?.detail || errorObj.message || 'Failed to process decision. Please try again.';
      setActionFeedback({
        type: 'error',
        message: detailMsg,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="p-6">
        <Link href="/dashboard/tickets" className="text-blue-600 hover:underline mb-4 inline-block">&larr; Back to Tickets</Link>
        <Card className="p-6 text-center text-red-600 bg-red-50 border-red-200">
          {error || 'Ticket not found.'}
        </Card>
      </div>
    );
  }

  const isPendingApproval = ticket.status.toUpperCase() === 'PENDING_APPROVAL';

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <Link href="/dashboard/tickets" className="text-blue-600 hover:underline inline-block">&larr; Back to Tickets</Link>
      
      {actionFeedback && (
        <div
          role={actionFeedback.type === 'error' ? 'alert' : 'status'}
          className={`p-4 rounded-lg border text-sm flex items-center justify-between ${
            actionFeedback.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-rose-50 text-rose-800 border-rose-200'
          }`}
        >
          <div className="flex items-center space-x-2">
            {actionFeedback.type === 'success' ? (
              <svg className="w-5 h-5 text-emerald-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-rose-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            )}
            <span className="font-medium">{actionFeedback.message}</span>
          </div>
          <button
            onClick={() => setActionFeedback(null)}
            className="text-gray-400 hover:text-gray-600 text-sm ml-4"
            aria-label="Dismiss feedback"
          >
            &times;
          </button>
        </div>
      )}

      {/* Staff Approval Actions Card */}
      {isStaff && isPendingApproval && (
        <Card className="p-6 border-purple-200 bg-purple-50/50 shadow-sm">
          <div className="sm:flex sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-purple-600"></span>
                </span>
                <h3 className="text-base font-semibold text-gray-900">Approval Required</h3>
              </div>
              <p className="mt-1 text-sm text-gray-600">
                This request is pending authorization. As IT Support / Administrator, you can review and approve or reject this decision.
              </p>
            </div>

            {!confirmAction && (
              <div className="mt-4 sm:mt-0 sm:ml-6 flex items-center space-x-3 shrink-0">
                <button
                  type="button"
                  id="approve-ticket-btn"
                  onClick={() => setConfirmAction('approve')}
                  disabled={isSubmitting}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 transition-colors cursor-pointer"
                >
                  Approve Request
                </button>
                <button
                  type="button"
                  id="reject-ticket-btn"
                  onClick={() => setConfirmAction('reject')}
                  disabled={isSubmitting}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-rose-700 bg-white hover:bg-rose-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 disabled:opacity-50 transition-colors cursor-pointer"
                >
                  Reject Request
                </button>
              </div>
            )}
          </div>

          {/* Decision Confirmation Dialog */}
          {confirmAction && (
            <div className="mt-4 pt-4 border-t border-purple-200" role="region" aria-label="Approval confirmation">
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <h4 className="text-sm font-semibold text-gray-900">
                  {confirmAction === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
                </h4>
                <p className="mt-1 text-sm text-gray-600">
                  {confirmAction === 'approve'
                    ? `Are you sure you want to approve ticket #${ticket.id}? The ticket will transition to APPROVED status.`
                    : `Are you sure you want to reject ticket #${ticket.id}? The ticket will transition to REJECTED status.`}
                </p>
                <div className="mt-4 flex items-center space-x-3">
                  <button
                    type="button"
                    id="confirm-decision-btn"
                    onClick={() => handleDecision(confirmAction)}
                    disabled={isSubmitting}
                    className={`inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white shadow-sm disabled:opacity-50 transition-colors cursor-pointer ${
                      confirmAction === 'approve'
                        ? 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500'
                        : 'bg-rose-600 hover:bg-rose-700 focus:ring-rose-500'
                    }`}
                  >
                    {isSubmitting
                      ? confirmAction === 'approve' ? 'Approving...' : 'Rejecting...'
                      : confirmAction === 'approve' ? 'Yes, Approve' : 'Yes, Reject'}
                  </button>
                  <button
                    type="button"
                    id="cancel-decision-btn"
                    onClick={() => setConfirmAction(null)}
                    disabled={isSubmitting}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Ticket Details Card */}
      <Card className="overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200 bg-gray-50 flex justify-between items-start">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h2 className="text-xl font-bold text-gray-900">#{ticket.id}</h2>
              <h1 className="text-xl font-bold text-gray-900">{ticket.title}</h1>
            </div>
            <p className="text-sm text-gray-500">
              Created on {new Date(ticket.created_at).toLocaleString()}
            </p>
          </div>
          <div className="flex flex-col space-y-2 items-end">
            <Badge color={getStatusColor(ticket.status)}>{formatStatus(ticket.status)}</Badge>
            <Badge color={getPriorityColor(ticket.priority)}>{ticket.priority}</Badge>
          </div>
        </div>
        
        <div className="px-6 py-6">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Description</h3>
          <div className="prose max-w-none text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-md border border-gray-100">
            {ticket.description}
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-sm text-gray-500">
          Last updated: {new Date(ticket.updated_at).toLocaleString()}
        </div>
      </Card>
    </div>
  );
}

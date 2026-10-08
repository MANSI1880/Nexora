'use client';

import React, { useEffect, useState } from 'react';
import { ticketsApi } from '@/lib/tickets';
import { TicketResponse } from '@/types/api';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import Link from 'next/link';

export default function TicketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [ticket, setTicket] = useState<TicketResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const unwrappedParams = React.use(params);
  const ticketId = unwrappedParams.id;

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const data = await ticketsApi.getById(ticketId);
        setTicket(data);
      } catch (err: unknown) {
        setError('Unable to load ticket details. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTicket();
  }, [ticketId]);

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'OPEN': return 'blue';
      case 'IN_PROGRESS': return 'yellow';
      case 'RESOLVED': return 'green';
      case 'CLOSED': return 'gray';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'HIGH': return 'red';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'blue';
      default: return 'gray';
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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Link href="/dashboard/tickets" className="text-blue-600 hover:underline mb-6 inline-block">&larr; Back to Tickets</Link>
      
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
            <Badge color={getStatusColor(ticket.status)}>{ticket.status}</Badge>
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

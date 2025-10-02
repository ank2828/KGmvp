'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { SyncStatus } from '@/types/api';
import Link from 'next/link';

export default function SettingsPage() {
  const [gmailSyncing, setGmailSyncing] = useState(false);
  const [hubspotSyncing, setHubspotSyncing] = useState(false);

  const { data: syncStatus, refetch } = useQuery<{ data: SyncStatus }>({
    queryKey: ['sync-status'],
    queryFn: () => api.sync.getStatus(),
    refetchInterval: 5000,
  });

  const handleConnectGmail = async () => {
    try {
      const { data } = await api.auth.getConnectToken();
      const connectUrl = new URL(data.connectLinkUrl);
      connectUrl.searchParams.set('app', 'gmail');

      const popup = window.open(
        connectUrl.toString(),
        'pipedream-oauth',
        'width=600,height=700'
      );

      const checkInterval = setInterval(async () => {
        if (popup?.closed) {
          clearInterval(checkInterval);
          refetch();
          setTimeout(() => {
            if (syncStatus?.data?.gmail?.connected) {
              alert('✅ Gmail connected!');
              handleSyncGmail();
            }
          }, 1000);
        }
      }, 500);
    } catch (error) {
      console.error('Failed to connect Gmail:', error);
      alert('❌ Failed to connect Gmail.');
    }
  };

  const handleConnectHubSpot = async () => {
    try {
      const { data } = await api.auth.getConnectToken();
      const connectUrl = new URL(data.connectLinkUrl);
      connectUrl.searchParams.set('app', 'hubspot');

      const popup = window.open(
        connectUrl.toString(),
        'pipedream-oauth',
        'width=600,height=700'
      );

      const checkInterval = setInterval(async () => {
        if (popup?.closed) {
          clearInterval(checkInterval);
          refetch();
          setTimeout(() => {
            if (syncStatus?.data?.hubspot?.connected) {
              alert('✅ HubSpot connected!');
              handleSyncHubSpot();
            }
          }, 1000);
        }
      }, 500);
    } catch (error) {
      console.error('Failed to connect HubSpot:', error);
      alert('❌ Failed to connect HubSpot.');
    }
  };

  const handleSyncGmail = async () => {
    setGmailSyncing(true);
    try {
      const response = await api.sync.syncGmail();
      alert(`✓ Gmail synced! ${response.data.synced} emails processed.`);
      refetch();
    } catch (error: any) {
      console.error('Sync failed:', error);
      alert(`Sync failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGmailSyncing(false);
    }
  };

  const handleSyncHubSpot = async () => {
    setHubspotSyncing(true);
    try {
      const response = await api.sync.syncHubSpot();
      alert(`✓ HubSpot synced! ${response.data.synced} items processed.`);
      refetch();
    } catch (error: any) {
      console.error('Sync failed:', error);
      alert(`Sync failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setHubspotSyncing(false);
    }
  };

  const gmailConnected = syncStatus?.data?.gmail?.connected || false;
  const hubspotConnected = syncStatus?.data?.hubspot?.connected || false;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Settings</h1>
        <Link
          href="/"
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          Back to Chat
        </Link>
      </header>

      <div className="p-8 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Integrations</h2>
        <p className="text-gray-600 mb-8">
          Connect your apps to sync data into the knowledge graph
        </p>

        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center text-2xl">
                  📧
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Gmail</h3>
                  <p className="text-sm text-gray-600">
                    Sync your emails to the knowledge graph
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                {!gmailConnected ? (
                  <button
                    onClick={handleConnectGmail}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                  >
                    Connect
                  </button>
                ) : (
                  <>
                    <span className="px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
                      ✓ Connected
                    </span>
                    <button
                      onClick={handleSyncGmail}
                      disabled={gmailSyncing}
                      className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      {gmailSyncing ? 'Syncing...' : 'Sync Now'}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-2xl">
                  🔶
                </div>
                <div>
                  <h3 className="font-semibold text-lg">HubSpot</h3>
                  <p className="text-sm text-gray-600">
                    Sync contacts, deals, and companies
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                {!hubspotConnected ? (
                  <button
                    onClick={handleConnectHubSpot}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                  >
                    Connect
                  </button>
                ) : (
                  <>
                    <span className="px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
                      ✓ Connected
                    </span>
                    <button
                      onClick={handleSyncHubSpot}
                      disabled={hubspotSyncing}
                      className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      {hubspotSyncing ? 'Syncing...' : 'Sync Now'}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

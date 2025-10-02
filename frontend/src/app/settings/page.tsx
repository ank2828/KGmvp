'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { SyncStatus } from '@/types/api';
import Link from 'next/link';

export default function SettingsPage() {
  const [gmailSyncing, setGmailSyncing] = useState(false);
  const [hubspotSyncing, setHubspotSyncing] = useState(false);

  // Fetch sync status
  const { data: syncStatus, refetch } = useQuery<{ data: SyncStatus }>({
    queryKey: ['sync-status'],
    queryFn: () => api.sync.getStatus(),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const handleConnectGmail = async () => {
    try {
      // Step 1: Get Pipedream Connect token from backend
      const { data } = await api.auth.getConnectToken();

      // Step 2: Initialize Pipedream SDK
      const { default: Pipedream } = await import('@pipedream/sdk');
      const pd = new Pipedream({
        connectToken: data.token,
      });

      // Step 3: Open OAuth modal for Gmail
      const account = await pd.connectAccount('gmail');

      // Step 4: Save connected account to backend
      await api.integrations.saveGmailAccount(account.id);

      // Refresh status
      refetch();

      // Auto-trigger initial sync
      handleSyncGmail();

    } catch (error) {
      console.error('Failed to connect Gmail:', error);
      alert('Failed to connect Gmail. Check console for details.');
    }
  };

  const handleConnectHubSpot = async () => {
    try {
      // Step 1: Get Pipedream Connect token from backend
      const { data } = await api.auth.getConnectToken();

      // Step 2: Initialize Pipedream SDK
      const { default: Pipedream } = await import('@pipedream/sdk');
      const pd = new Pipedream({
        connectToken: data.token,
      });

      // Step 3: Open OAuth modal for HubSpot
      const account = await pd.connectAccount('hubspot');

      // Step 4: Save connected account to backend
      await api.integrations.saveHubSpotAccount(account.id);

      // Refresh status
      refetch();

      // Auto-trigger initial sync
      handleSyncHubSpot();

    } catch (error) {
      console.error('Failed to connect HubSpot:', error);
      alert('Failed to connect HubSpot. Check console for details.');
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
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Settings</h1>
        <Link
          href="/"
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          Back to Chat
        </Link>
      </header>

      {/* Content */}
      <div className="p-8 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Integrations</h2>
        <p className="text-gray-600 mb-8">
          Connect your apps to sync data into the knowledge graph
        </p>

        <div className="space-y-6">
          {/* Gmail Card */}
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
                  {gmailConnected && syncStatus?.data?.gmail?.last_sync && (
                    <p className="text-xs text-gray-500 mt-1">
                      Last synced: {new Date(syncStatus.data.gmail.last_sync).toLocaleString()}
                    </p>
                  )}
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

          {/* HubSpot Card */}
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
                  {hubspotConnected && syncStatus?.data?.hubspot?.last_sync && (
                    <p className="text-xs text-gray-500 mt-1">
                      Last synced:{' '}
                      {new Date(syncStatus.data.hubspot.last_sync).toLocaleString()}
                    </p>
                  )}
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

        {/* Info Box */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">How it works</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>1. Click "Connect" to authorize access via OAuth</li>
            <li>2. Click "Sync Now" to fetch data from the last 3 months</li>
            <li>3. Data is processed into episodes and stored in the knowledge graph</li>
            <li>4. Ask questions in the chat interface!</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

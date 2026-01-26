/**
 * Backend Connection Test
 * Run: node test-backend-connection.js
 */

const BACKEND_URL = 'http://localhost:8000';

async function testBackend() {
  console.log('🧪 Testing Backend Connection...\n');

  // Test 1: Root endpoint
  console.log('1️⃣ Testing root endpoint /');
  try {
    const res = await fetch(`${BACKEND_URL}/`);
    const data = await res.json();
    console.log('✅ Root endpoint:', data);
  } catch (error) {
    console.error('❌ Root endpoint failed:', error.message);
    return;
  }

  // Test 2: Health check
  console.log('\n2️⃣ Testing health endpoint /api/health');
  try {
    const res = await fetch(`${BACKEND_URL}/api/health`);
    const data = await res.json();
    console.log('✅ Health check:', data);
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return;
  }

  // Test 3: Query endpoint
  console.log('\n3️⃣ Testing query endpoint /api/query');
  try {
    const payload = {
      question: 'What is Physical AI?',
      top_k: 5,
      include_context: true
    };

    console.log('Request payload:', JSON.stringify(payload, null, 2));

    const res = await fetch(`${BACKEND_URL}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const error = await res.json();
      console.error('❌ Query failed:', res.status, error);
      return;
    }

    const data = await res.json();
    console.log('✅ Query succeeded:');
    console.log('  - Question:', data.question);
    console.log('  - Context length:', data.context?.length || 0, 'chars');
    console.log('  - Sources:', data.sources?.length || 0);
    console.log('  - Metadata:', data.metadata);
  } catch (error) {
    console.error('❌ Query failed:', error.message);
    return;
  }

  console.log('\n✅ All tests passed!');
}

testBackend();

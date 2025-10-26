// CloudFlare Worker برای API
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Route handling
    if (path.startsWith('/api/')) {
      return handleAPI(request, path);
    }

    // Serve static files
    return serveStatic(request);
  }
}

async function handleAPI(request, path) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // API routes simulation
  if (path === '/api/clients/plans') {
    return jsonResponse({
      success: true,
      plans: {
        free: { monthly_price: 0, conversion_quota: 10 },
        basic: { monthly_price: 29, conversion_quota: 100 },
        professional: { monthly_price: 99, conversion_quota: 500 },
        enterprise: { monthly_price: 299, conversion_quota: 2000 }
      }
    }, corsHeaders);
  }

  if (path === '/api/convert/start' && request.method === 'POST') {
    return jsonResponse({
      success: true,
      message: "Conversion started (CloudFlare Worker)",
      conversion_id: "cf_" + Date.now()
    }, corsHeaders);
  }

  return jsonResponse({ error: 'Endpoint not found' }, corsHeaders, 404);
}

function jsonResponse(data, headers = {}, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 
      'Content-Type': 'application/json',
      ...headers 
    }
  });
}

async function serveStatic(request) {
  // اینجا فایل‌های استاتیک سرو می‌شوند
  return new Response('Static file serving would be implemented');
}

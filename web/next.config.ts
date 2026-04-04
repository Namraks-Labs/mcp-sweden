import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  rewrites: async () => [
    {
      source: "/mcp/:path*",
      destination: `${process.env.MCP_SERVER_URL || "http://mcp-sweden.railway.internal:8000"}/mcp/:path*`,
    },
  ],
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Remove appFolder - App Router is default
  },
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'base:app_id',
          value: '69585539c63ad876c9081e3f',
        },
      ],
    },
  ],
};

export default nextConfig;

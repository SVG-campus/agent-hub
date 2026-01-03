/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appFolder: true
  },
  env: {
    BASE_APP_ID: process.env.BASE_APP_ID || '69585539c63ad876c9081e3f'
  }
};

export default nextConfig;

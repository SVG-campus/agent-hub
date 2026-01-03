import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Base Verifier',
  other: {
    'base:app_id': '69585539c63ad876c9081e3f',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

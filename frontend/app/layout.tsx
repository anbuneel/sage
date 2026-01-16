import type { Metadata } from "next";
import { Fraunces, Public_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const publicSans = Public_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SAGE — Smart Agentic Guide Engine",
  description: "AI-powered mortgage eligibility checker for Fannie Mae HomeReady and Freddie Mac Home Possible programs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${publicSans.variable} ${jetbrainsMono.variable} light`}
      style={{ colorScheme: 'light' }}
    >
      <body className="bg-paper text-ink-900 antialiased">
        {children}
      </body>
    </html>
  );
}

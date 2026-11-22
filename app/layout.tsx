import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "하늘꿈연동교회 회계관리", description: "부서별 회계관리" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}

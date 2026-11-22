import { notFound } from "next/navigation";
import AccountingApp from "@/app/AccountingApp";
import { GROUPS, parseGroup } from "@/lib/group";
import type { Metadata } from "next";

export async function generateMetadata({ params }: { params: Promise<{ group: string }> }): Promise<Metadata> {
  const group = parseGroup((await params).group);
  return { title: group ? `${GROUPS[group].name} 회계관리` : "회계관리" };
}

export default async function GroupPage({ params }: { params: Promise<{ group: string }> }) {
  const { group: rawGroup } = await params;
  const group = parseGroup(rawGroup);
  if (!group) notFound();
  return <AccountingApp group={group} />;
}

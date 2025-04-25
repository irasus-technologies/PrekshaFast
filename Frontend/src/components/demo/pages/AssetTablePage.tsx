"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ColumnDef } from "@tanstack/react-table";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/demo/tables/DataTable";
import { Download } from "lucide-react";


interface BulkAction {
    label: string;
    href: string;
}
interface AssetTablePageProps<TData> {
    title: string;
    header: string;
    subtitle: string;
    columns: ColumnDef<TData, any>[];
    data: TData[];
    breadcrumbs: { label: string; href?: string }[];
    visibleCols?: string[];
    clickableColumns?: string[];
    bulkActions?: BulkAction[];
}

export function AssetTablePage<TData>({
    title,
    header,
    subtitle,
    columns,
    data,
    breadcrumbs,
    visibleCols,
    bulkActions,
    clickableColumns,
}: AssetTablePageProps<TData>) {
    const pathname = usePathname(); // Gets current path like /vehicles
    const router = useRouter();
    const handleCreateClick = () => {
        router.push(`${pathname}/create`);
    };
    return (
        <ContentLayout title={title}>
            <Breadcrumb>
                <BreadcrumbList>
                    {breadcrumbs.map((crumb, index) => (
                        <div key={index} className="flex items-center">
                            <BreadcrumbItem>
                                {crumb.href ? (
                                    <BreadcrumbLink asChild>
                                        <Link href={crumb.href}>{crumb.label}</Link>
                                    </BreadcrumbLink>
                                ) : (
                                    <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                                )}
                            </BreadcrumbItem>
                            {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
                        </div>
                    ))}
                </BreadcrumbList>
            </Breadcrumb>

            <div className="max-w-7xl py-8 px-4 space-y-6 bg-background border rounded-md mt-2">
                <div>
                    <h1 className="text-3xl font-bold">{header}</h1>
                    <p className="text-muted-foreground text-sm">{subtitle}</p>
                </div>

                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <Input placeholder="Search" className="w-full max-w-sm" />
                    <div className="flex flex-wrap gap-2">
                        <Button variant="outline">
                            <Download className="w-4 h-4 mr-2" />
                            Download
                        </Button>
                        {/* <Button variant="outline">Filter</Button> */}
                        <Button onClick={handleCreateClick}>Create</Button>
                        <Button variant="outline">View Drivers</Button>
                        {bulkActions && bulkActions.length > 0 ? (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline">Bulk Actions</Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    {bulkActions.map((action, index) => (
                                        <DropdownMenuItem key={index} asChild>
                                            <Link href={action.href}>{action.label}</Link>
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        ) : (
                            <Button variant="outline" disabled>
                                Bulk Actions
                            </Button>
                        )}
                    </div>
                </div>

                <DataTable
                    columns={columns}
                    data={data}
                    loading={false}
                    enableSearch={false}
                    enableMultiSelect
                    enableColumnToggle
                    enableRowActions
                    visibleCols={visibleCols}
                    clickableColumns={clickableColumns}

                />
            </div>
        </ContentLayout>
    );
}

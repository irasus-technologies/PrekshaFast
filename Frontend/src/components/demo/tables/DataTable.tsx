import React, { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, ArrowDown } from "lucide-react";
import {
    useReactTable,
    ColumnDef,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    flexRender,
    SortingState,
} from "@tanstack/react-table";
import {
    Table, TableBody, TableCell, TableFooter, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuContent
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
    Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger
} from "@/components/ui/dialog";

interface TableProps<TData> {
    columns: ColumnDef<TData, any>[];
    data: TData[];
    loading: boolean;
    enableSearch?: boolean;
    enableMultiSelect?: boolean;
    enableColumnToggle?: boolean;
    enableRowActions?: boolean;
    visibleCols?: string[];
}

export function DataTable<TData>({
    columns,
    data,
    enableSearch = false,
    enableMultiSelect = false,
    enableColumnToggle = false,
    enableRowActions = false,
    visibleCols,
    loading = false,
}: TableProps<TData>) {
    const [search, setSearch] = useState("");
    const selectAllRef = useRef<HTMLInputElement | null>(null);
    const [selectedRows, setSelectedRows] = useState<Record<string, boolean>>({});
    const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>({});
    const [sorting, setSorting] = useState<SortingState>([]);
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });
    const filteredData = useMemo(() => {
        if (!search) return data;

        return data.filter((row, index) =>
            columns.some((column) => {
                // Check if the column has either accessorKey or accessorFn
                if ('accessorKey' in column && column.accessorKey) {
                    // Using accessorKey
                    const cellValue = row[column.accessorKey as keyof TData];
                    return cellValue && cellValue.toString().toLowerCase().includes(search.toLowerCase());
                } else if ('accessorFn' in column && column.accessorFn) {
                    // Using accessorFn and passing both row and index
                    const cellValue = column.accessorFn(row, index);
                    return cellValue && cellValue.toString().toLowerCase().includes(search.toLowerCase());
                }
                return false;
            })
        );
    }, [data, search, columns]);

    console.log(filteredData)
    // Set default column visibility based on `visibleCols` prop
    useEffect(() => {
        if (visibleCols) {
            const defaultVisibility = columns.reduce((acc, column) => {
                // Check if 'accessorKey' exists on the column
                if ("accessorKey" in column && column.accessorKey) {
                    acc[column.accessorKey as string] = visibleCols.includes(column.accessorKey as string);
                }
                return acc;
            }, {} as Record<string, boolean>);
            setColumnVisibility(defaultVisibility);
        } else {
            const defaultVisibility = columns.reduce((acc, column) => {
                // Check if 'accessorKey' exists on the column
                if ("accessorKey" in column && column.accessorKey) {
                    acc[column.accessorKey as string] = true;
                }
                return acc;
            }, {} as Record<string, boolean>);
            setColumnVisibility(defaultVisibility);
        }
    }, [columns, visibleCols]);


    // Configure the table with React Table hooks
    const table = useReactTable({
        data,
        columns,
        state: { columnVisibility, sorting, pagination },
        onPaginationChange: setPagination,
        onSortingChange: setSorting,
        onColumnVisibilityChange: setColumnVisibility,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        pageCount: Math.ceil(data.length / pagination.pageSize),
    });

    const toggleRowSelection = (id: string) => {
        setSelectedRows((prev) => ({ ...prev, [id]: !prev[id] }));
    };

    const toggleSelectAll = () => {
        const isAllSelected = table.getRowModel().rows.every((row) => selectedRows[row.id]);
        const newSelectedRows = table.getRowModel().rows.reduce((acc, row) => {
            acc[row.id] = !isAllSelected;
            return acc;
        }, {} as Record<string, boolean>);
        setSelectedRows(newSelectedRows);
    };

    useEffect(() => {
        if (selectAllRef.current) {
            const isAllSelected = table.getRowModel().rows.every((row) => selectedRows[row.id]);
            const isSomeSelected =
                table.getRowModel().rows.some((row) => selectedRows[row.id]) && !isAllSelected;
            selectAllRef.current.indeterminate = isSomeSelected;
        }
    }, [selectedRows, table]);

    return (
        <div>
            {enableSearch && (
                <div className="mb-4">
                    <Input
                        placeholder="Search..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            )}

            {enableColumnToggle && (
                <Dialog>
                    <DialogTrigger asChild>
                        <Button className="bg-blue-500 text-white">Toggle Columns</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Toggle Column Visibility</DialogTitle>
                            <DialogDescription>
                                Select the columns you want to show or hide.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                            {table.getAllColumns().map((column) => (
                                <div key={column.id}>
                                    <label className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            className="checkbox"
                                            checked={column.getIsVisible()}
                                            onChange={column.getToggleVisibilityHandler()}
                                        />
                                        <span>{column.id}</span>
                                    </label>
                                </div>
                            ))}
                        </div>
                    </DialogContent>
                </Dialog>
            )}

            <Table className="border border-[#D8D8D8] rounded-md bg-white">
                <TableHeader className="bg-background hover:bg-gray-900">
                    {table.getHeaderGroups().map((headerGroup) => (
                        <TableRow key={headerGroup.id}>
                            {enableMultiSelect && (
                                <TableHead>
                                    <Checkbox
                                        checked={table.getRowModel().rows.every((row) => selectedRows[row.id])}
                                        onCheckedChange={toggleSelectAll}
                                        className="bg-white"
                                    />
                                </TableHead>
                            )}
                            {headerGroup.headers.map((header) => (
                                <TableHead
                                    key={header.id}
                                    onClick={header.column.getToggleSortingHandler()}
                                    className="cursor-pointer py-3 text-white"
                                >
                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                    <span className="ml-2">
                                        <ArrowUp
                                            className={`inline-block w-3 h-3 ${header.column.getIsSorted() === "asc" ? "text-black" : "text-gray-300"}`}
                                        />
                                        <ArrowDown
                                            className={`inline-block w-3 h-3 ${header.column.getIsSorted() === "desc" ? "text-black" : "text-gray-300"}`}
                                        />
                                    </span>
                                </TableHead>
                            ))}
                            {enableRowActions && <TableHead className="sticky right-0 z-10 ">Actions</TableHead>}
                        </TableRow>
                    ))}
                </TableHeader>
                <TableBody>
                    {loading ? (
                        <TableRow>
                            <TableCell colSpan={columns.length + (enableMultiSelect ? 1 : 0)} className="text-center">
                                Loading...
                            </TableCell>
                        </TableRow>
                    ) : table.getRowModel().rows.length > 0 ? (
                        table.getRowModel().rows.map((row) => (
                            <TableRow key={row.id}>
                                {enableMultiSelect && (
                                    <TableCell>
                                        <Checkbox
                                            checked={!!selectedRows[row.id]}
                                            onCheckedChange={() => toggleRowSelection(row.id)}
                                        />
                                    </TableCell>
                                )}
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id}>
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </TableCell>
                                ))}
                                {enableRowActions && (
                                    <TableCell className="sticky right-0 z-10 bg-white">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button>...</Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent>
                                                <DropdownMenuItem onClick={() => console.log("Edit", row.id)}>
                                                    Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => console.log("Delete", row.id)}>
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                )}
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={columns.length + (enableMultiSelect ? 1 : 0)} className="text-center">
                                No data found.
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>

            {/* Pagination */}
            <div className="flex justify-between py-4">
                <div className="flex items-center space-x-2">
                    <span>Rows per page</span>
                    <Select
                        onValueChange={(value) => setPagination((prev) => ({ ...prev, pageSize: Number(value) }))}
                        defaultValue={`${pagination.pageSize}`}
                    >
                        <SelectTrigger className="w-[80px]">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="5">5</SelectItem>
                            <SelectItem value="10">10</SelectItem>
                            <SelectItem value="20">20</SelectItem>
                            <SelectItem value="50">50</SelectItem>
                        </SelectContent>
                    </Select>
                    <span>
                        Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                    </span>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        onClick={() => table.setPageIndex(0)}
                        disabled={!table.getCanPreviousPage()}
                    >
                        {"<<"}
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => table.previousPage()}
                        disabled={!table.getCanPreviousPage()}
                    >
                        {"<"}
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => table.nextPage()}
                        disabled={!table.getCanNextPage()}
                    >
                        {">"}
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                        disabled={!table.getCanNextPage()}
                    >
                        {">>"}
                    </Button>
                </div>
            </div>
        </div>
    );
}

import {
  Bike,
  MemoryStick,
  BatteryCharging,
  Plug,
  Cross,
  Calendar,
  BarChart3,
  Repeat,
  Rows2,
  LineChart,
  LayoutDashboard,
  LayoutGrid,
  MapPin,
  ClipboardList,
  Users,
  LifeBuoy,
  Home,
} from "lucide-react";
import { LucideIcon } from "lucide-react";

type Submenu = {
  href: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
};

type Menu = {
  href: string;
  label: string;
  active?: boolean;
  icon: LucideIcon;
  submenus?: Submenu[];
};

type Group = {
  groupLabel: string;
  menus: Menu[];
};

export function getMenuList(pathname: string): Group[] {
  return [
    {
      groupLabel: "Assets",
      menus: [
        {
          href: "/vehicles",
          label: "Vehicles",
          active: pathname === "/vehicles",
          icon: Bike,
        },
        {
          href: "/sim-cards",
          label: "SIM Cards",
          active: pathname === "/sim-cards",
          icon: MemoryStick,
        },
        {
          href: "/battery-packs",
          label: "Battery Packs",
          active: pathname === "/battery-packs",
          icon: BatteryCharging,
        },
        {
          href: "/chargers",
          label: "Chargers",
          active: pathname === "/chargers",
          icon: Plug,
        },
        {
          href: "/position-tracker",
          label: "Position Tracker",
          active: pathname.startsWith("/position-tracker"),
          icon: Cross,
          submenus: [
            {
              href: "/position-tracker/can",
              label: "Position Trackers CAN",
              icon: Calendar,
            },
            {
              href: "/position-tracker/basic",
              label: "Position Tracker Basic",
              icon: BarChart3,
            },
            
          ],
        },
        {
          href: "/swapping-stations",
              label: "Swapping Stations",
              icon: Repeat,
          active: pathname === "/swapping-stations",
         
        },
        {
          href: "/all-sets",
          label: "All Sets",
          active: pathname === "/all-sets",
          icon: Rows2,
        },
      ],
    },
    {
      groupLabel: "Dashboards",
      menus: [
        {
          href: "/dashboards",
          label: "Dashboards",
          active: pathname.startsWith("/dashboards"),
          icon: LayoutGrid,
          submenus: [
            {
              href: "/dashboards/battery-analytics",
              label: "Battery Analytics",
              icon: LineChart,
            },
            {
              href: "/dashboards/custom",
              label: "Custom Dashboards",
              icon: LayoutDashboard,
            },
            {
              href: "/dashboards/non-can",
              label: "Non-CAN Dashboard",
              icon: BarChart3,
            },
          ],
        },
      ],
    },
    {
      groupLabel: "",
      menus: [
        {
          href: "/locations",
          label: "Locations",
          active: pathname === "/locations",
          icon: MapPin,
        },
        {
          href: "/reports",
          label: "Reports",
          active: pathname === "/reports",
          icon: ClipboardList,
        },
        {
          href: "/users",
          label: "Users",
          active: pathname === "/users",
          icon: Users,
        },
        {
          href: "/support",
          label: "Support",
          active: pathname === "/support",
          icon: LifeBuoy,
        },
      ],
    },
  ];
}

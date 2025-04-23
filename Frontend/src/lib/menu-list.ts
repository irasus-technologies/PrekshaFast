import {
  Tag,
  Users,
  Settings,
  Bookmark,
  SquarePen,
  LayoutGrid,
  LucideIcon,
  Home,
  LineChart,
  Siren,
  ClipboardList,
} from "lucide-react";

type Submenu = {
  href: string;
  label: string;
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
      groupLabel: "",
      menus: [
        {
          href: "/dashboard",
          label: "Home",
          active: pathname.includes("/dashboard"),
          icon:   Home,

          submenus: []
        }
      ]
    },
    {
      groupLabel: "Contents",
      menus: [
        {
          href: "",
          label: "Assets",
          active: pathname.includes("/posts"),
          icon: LineChart,
          submenus: [
            {
              href: "/vehicles",
              label: "Vehicles"
            },
            {
              href: "/battery-pack",
              label: "Battery Packs"
            }
          ]
        },
        {
          href: "/categories",
          label: "Alerts",
          active: pathname.includes("/categories"),
          icon: Siren
        },
        {
          href: "/tags",
          label: "reports",
          active: pathname.includes("/tags"),
          icon: ClipboardList
        }
      ]
    },
    {
      groupLabel: "Settings",
      menus: [
        {
          href: "/users",
          label: "Users",
          active: pathname.includes("/users"),
          icon: Users
        },
        {
          href: "/account",
          label: "Settings",
          active: pathname.includes("/account"),
          icon: Settings
        }
      ]
    }
  ];
}

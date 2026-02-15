import HomePage from "../pages/HomePage";
import BooksPage from "../pages/BooksPage";
import MembersPage from "../pages/MembersPage";
import BorrowPage from "../pages/BorrowPage";
import LoginPage from "../pages/LoginPage";

/**
 * Route path constants
 */
export const ROUTE_PATHS = {
  HOME: "/",
  LOGIN: "/login",
  BOOKS: "/books",
  MEMBERS: "/members",
  BORROW: "/borrow",
};

/**
 * Route configuration
 * Each route specifies path, component, and whether it requires authentication
 */
export const ROUTES = [
  {
    path: ROUTE_PATHS.LOGIN,
    component: LoginPage,
    isProtected: false,
  },
  {
    path: ROUTE_PATHS.HOME,
    component: HomePage,
    isProtected: true,
  },
  {
    path: ROUTE_PATHS.BOOKS,
    component: BooksPage,
    isProtected: true,
  },
  {
    path: ROUTE_PATHS.MEMBERS,
    component: MembersPage,
    isProtected: true,
  },
  {
    path: ROUTE_PATHS.BORROW,
    component: BorrowPage,
    isProtected: true,
  },
];

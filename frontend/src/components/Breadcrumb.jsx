import { ChevronRight, Home } from "lucide-react";
import { Link } from "react-router-dom";

function Breadcrumbs({ items = [] }) {
  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse">
        <li className="inline-flex items-center">
          <Link
            to="/chat"
            className="inline-flex items-center text-sm font-medium text-body hover:text-fg-brand"
          >
            <Home className="h-4 w-4" />
          </Link>
        </li>

        {items.map((item, index) => (
          <li
            key={index}
            className="flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse"
          >
            <ChevronRight className="h-4 w-4" />
            <Link to={item.href} className="hover:text-indigo-500">
              {item.name}
            </Link>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export default Breadcrumbs;

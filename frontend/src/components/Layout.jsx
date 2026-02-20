import { Link, useLocation } from 'react-router-dom';
import { Video, Upload, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../utils/helpers';

export default function Layout({ children }) {
  const location = useLocation();

  const pathParts = location.pathname.split('/');
  const urlTaskId = (pathParts[1] === 'status' || pathParts[1] === 'results') ? pathParts[2]:null;
  const savedTaskId = typeof window !== 'undefined' ? localStorage.getItem('streamscale_active_task') : null;

  const activeTaskId = urlTaskId || savedTaskId;

  const statusTarget = activeTaskId ? `/status/${activeTaskId}` : '/status';

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-dark-border bg-dark-card/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <Link to="/" className="flex items-center gap-3 group">
              <motion.div 
                className="w-10 h-10 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-lg flex items-center justify-center"
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: 'spring', stiffness: 400 }}
              >
                <Video className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight font-display">
                  StreamScale
                </h1>
                <p className="text-xs text-gray-500">Distributed Transcoding</p>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              <NavLink to="/" icon={Upload} active={location.pathname === '/'}>
                Upload
              </NavLink>
              <NavLink to={statusTarget} icon={Activity} active={location.pathname.startsWith('/status')}>
                Status
              </NavLink>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-dark-border mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              © 2026 StreamScale.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function NavLink({ to, icon: Icon, active, children }) {
  return (
    <Link
      to={to}
      className={cn(
        'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all',
        active
          ? 'bg-accent-primary/10 text-accent-primary'
          : 'text-gray-400 hover:text-white hover:bg-dark-hover'
      )}
    >
      <Icon className="w-4 h-4" />
      {children}
    </Link>
  );
}

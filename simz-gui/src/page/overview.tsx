import { ChevronRight, DatabaseIcon, File, Plus, Settings } from 'lucide-react';
import OverviewCard from '@/components/default/overview/overviewbtncard';
import { DataTableDemo } from '@/components/default/overview/projecttable';

export default function OverviewPage() {

  const handleNewProject = () => {
    console.log('New project clicked');
    // Add your project creation logic here
  };

  return (
    <div className='flex flex-col my-10 mx-5'>
      <div className='grid lg:grid-cols-4 md:grid-cols-2 sm:grid-cols-1 gap-4 mb-10'>
        <OverviewCard
          mainicon={File}
          secicon={Plus}
          label='New Project'
          onClick={handleNewProject}
        />
        <OverviewCard
          mainicon={DatabaseIcon}
          secicon={ChevronRight}
          label='Data Source'
          onClick={handleNewProject}
        />
        <OverviewCard
          mainicon={Settings}
          secicon={ChevronRight}
          label='Settings'
          onClick={handleNewProject}
        />
      </div>
      <div className='felx flex-row mb-5' >
        <h1 className='text-4xl font-semibold text-slate-800' >All Projects</h1>
        {/* <hr className='my-5' /> */}
      </div>
      <div className='felx'>
        <DataTableDemo />
      </div>

    </div>
  );
}

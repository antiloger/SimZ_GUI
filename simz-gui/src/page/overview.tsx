import { ChevronRight, DatabaseIcon, File, Plus, Settings } from 'lucide-react';
import OverviewCard from '@/components/default/overview/overviewbtncard';
import { DataTableDemo } from '@/components/default/overview/projecttable';
import { useSocketStore } from '@/utils/socketIo';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import ProjectCreateDialog from '@/components/default/overview/createProjectDialog';
import { ProjectList } from '@/types/projects';

export default function OverviewPage() {
  const [projectTableData, setProjectTableData] = useState<ProjectList[]>([]);
  const { connected, ping, get_project_list } = useSocketStore();
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const OpenCreateProject = () => {
    setCreateDialogOpen(true)
  }
  const handleNewProject = () => {
    console.log('New project clicked');
    // Add your project creation logic here
  };

  const getDataToProjectTable = async () => {
    const response = await get_project_list();
    setProjectTableData(response.projects);
  }

  useEffect(() => {
    getDataToProjectTable();
  }, [connected]);


  const refresh = () => {
    getDataToProjectTable();
  }


  return (
    <>
      <div className='flex flex-col my-10 mx-5'>
        <div className='flex flex-row w-full' >
          <div className='flex flex-row justify-between w-full' >
            {
              connected ? ("Connected") : ("Disconnected")
            }
          </div>
          <div className='flex' >
            <Button onClick={() => { ping() }}>
              ping
            </Button>
          </div>
        </div>
        <div className='grid lg:grid-cols-4 md:grid-cols-2 sm:grid-cols-1 gap-4 mb-10'>
          <OverviewCard
            mainicon={File}
            secicon={Plus}
            label='New Project'
            onClick={() => { OpenCreateProject() }}
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
          <DataTableDemo data={projectTableData} />
        </div>

      </div>
      <ProjectCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} refresh={refresh} />
    </>
  );
}

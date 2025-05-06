import { ChevronRight, Codesandbox, File, Plus, Settings } from 'lucide-react';
import OverviewCard from '@/components/default/overview/overviewbtncard';
import { DataTableDemo } from '@/components/default/overview/projecttable';
import { useSocketStore } from '@/utils/socketIo';
import { useEffect, useState } from 'react';
import ProjectCreateDialog from '@/components/default/overview/createProjectDialog';
import { ProjectList } from '@/types/projects';
import { Badge } from '@/components/ui/badge';

export default function OverviewPage() {
  const [projectTableData, setProjectTableData] = useState<ProjectList[]>([]);
  const { connected, get_project_list } = useSocketStore();
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
      <div className='flex flex-col '>
        <div className='flex flex-row w-full items-center justify-between p-2 border-b mb-6' >
          <div className='flex flex-row items-center ' >
            <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <Codesandbox className="size-4" />
            </div>
            <div className='flex  ml-2' >
              <h1 className='text-2xl font-semibold text-slate-800' >SimZ</h1>
            </div>
          </div>
          <div className='flex' >
            {
              connected ? (
                <Badge className='bg-green-400 ' >connected</Badge>
              ) : (
                <Badge className='bg-red-300 '  >disconneced</Badge>
              )
            }
          </div>
        </div>
        <div className='grid lg:grid-cols-4 md:grid-cols-2 sm:grid-cols-1 gap-4 mb-10 mx-5'>
          <OverviewCard
            mainicon={File}
            secicon={Plus}
            label='New Project'
            onClick={() => { OpenCreateProject() }}
          />
          {/* <OverviewCard */}
          {/*   mainicon={DatabaseIcon} */}
          {/*   secicon={ChevronRight} */}
          {/*   label='Data Source' */}
          {/*   onClick={handleNewProject} */}
          {/* /> */}
          <OverviewCard
            mainicon={Settings}
            secicon={ChevronRight}
            label='Settings'
            onClick={handleNewProject}
          />
        </div>
        <div className='felx flex-row mb-5 mx-5' >
          <h1 className='text-4xl font-semibold text-slate-800' >All Projects</h1>
          {/* <hr className='my-5' /> */}
        </div>
        <div className='felx mx-5' >
          <DataTableDemo data={projectTableData} />
        </div>

      </div>
      <ProjectCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} refresh={refresh} />
    </>
  );
}

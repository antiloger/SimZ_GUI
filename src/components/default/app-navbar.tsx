import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Bell, ChevronDown, ChevronRight, HelpCircle, Menu, Settings, User } from "lucide-react"
import { useNavProjectState, useProjectOptState } from "@/state/nav-state"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

type MobileMenuProps = {
  views: string[];
  projectOptions: string[];
  selectedView: string;
  selectedProjectOption: string;
  setSelectedView: (view: string) => void;
  setSelectedProjectOption: (option: string) => void;
}

const MobileMenu: React.FC<MobileMenuProps> = ({
  views,
  projectOptions,
  selectedView,
  selectedProjectOption,
  setSelectedView,
  setSelectedProjectOption
}) => (
  <Sheet>
    <SheetTrigger asChild>
      <Button variant="ghost" size="icon" className="inline-flex items-center justify-center p-2 rounded-md text-gray-400">
        <Menu className="h-6 w-6" />
      </Button>
    </SheetTrigger>
    <SheetContent side="right" className="w-[300px] sm:w-[400px]">
      <nav className="flex flex-col gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="justify-start w-full">
              {selectedView}
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-full">
            {views.map((view) => (
              <DropdownMenuItem key={view} onSelect={() => setSelectedView(view)}>
                {view}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {selectedView !== 'Overview' && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="justify-start w-full">
                {selectedProjectOption}
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-full">
              {projectOptions.map((option) => (
                <DropdownMenuItem key={option} onSelect={() => setSelectedProjectOption(option)}>
                  {option}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        <hr className="my-2" />
        <Button variant="ghost" className="justify-start">
          <Bell className="h-5 w-5 mr-2" /> Notifications
        </Button>
        <Button variant="ghost" className="justify-start">
          <HelpCircle className="h-5 w-5 mr-2" /> Help
        </Button>
        <Button variant="ghost" className="justify-start">
          <Settings className="h-5 w-5 mr-2" /> Settings
        </Button>
        <Button variant="ghost" className="justify-start">
          <User className="h-5 w-5 mr-2" /> Profile
        </Button>
      </nav>
    </SheetContent>
  </Sheet>
)

type ViewSelectorProps = {
  selectedView: string;
  setSelectedView: (view: string) => void;
  views: string[];
}

const ViewSelector: React.FC<ViewSelectorProps> = ({ selectedView, setSelectedView, views }) => (
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button variant="ghost" className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700">
        {selectedView}
        <ChevronDown className="ml-2 h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      {views.map((view) => (
        <DropdownMenuItem key={view} onSelect={() => setSelectedView(view)}>
          {view}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  </DropdownMenu>
)

const ActionButtons: React.FC = () => (
  <>
    <Button variant="ghost" size="icon">
      <Bell className="h-5 w-5 text-gray-500" />
    </Button>
    <Button variant="ghost" size="icon">
      <HelpCircle className="h-5 w-5 text-gray-500" />
    </Button>
    <Button variant="ghost" size="icon">
      <Settings className="h-5 w-5 text-gray-500" />
    </Button>
    <Button variant="ghost" size="icon">
      <User className="h-5 w-5 text-gray-500" />
    </Button>
  </>
)

type ProjectSelectorProps = {
  selectedProjectOption: string;
  setSelectedProjectOption: (option: string) => void;
  projectOptions: string[];
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({ selectedProjectOption, setSelectedProjectOption, projectOptions }) => (
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button variant="ghost" className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700">
        {selectedProjectOption}
        <ChevronDown className="ml-2 h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      {projectOptions.map((option) => (
        <DropdownMenuItem key={option} onSelect={() => setSelectedProjectOption(option)}>
          {option}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  </DropdownMenu>
)

export default function AppNavBar() {
  const views = useNavProjectState((state) => state.btn);
  const selectedView = useNavProjectState((state) => state.selectedBtn);
  const setSelectedView = useNavProjectState((state) => state.setSelectedBtn);
  const selectedProjectOption = useProjectOptState((state) => state.selectedBtn);
  const setSelectedProjectOption = useProjectOptState((state) => state.setSelectedBtn);
  const projectOptions = useProjectOptState((state) => state.cat);

  return (
    <nav className="bg-white border-b border-gray-200 w-full">
      <div className=" px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-green-600">Zimula</span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-4">
              <ViewSelector selectedView={selectedView} setSelectedView={setSelectedView} views={views} />
              {selectedView !== 'Overview' && (
                <>
                  <ChevronRight />
                  <ProjectSelector
                    selectedProjectOption={selectedProjectOption}
                    setSelectedProjectOption={setSelectedProjectOption}
                    projectOptions={projectOptions}
                  />
                </>
              )}
            </div>
          </div>
          <div className="hidden sm:flex items-center space-x-4">
            <ActionButtons />
          </div>
          <div className="flex items-center sm:hidden">
            <MobileMenu
              views={views}
              projectOptions={projectOptions}
              selectedView={selectedView}
              selectedProjectOption={selectedProjectOption}
              setSelectedView={setSelectedView}
              setSelectedProjectOption={setSelectedProjectOption}
            />
          </div>
        </div>
      </div>
    </nav>
  )
}

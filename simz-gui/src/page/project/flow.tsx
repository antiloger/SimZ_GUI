import Flow from '@/components/default/ReactFlow/flow'
import PropertySheet from '@/components/default/ReactFlow/propertySheet';

function FlowPage() {
  return (
    <div className='flex flex-col' >
      {/* <div> <MainMenubar /> </div> */}
      <div>
        <Flow />
        <PropertySheet />
      </div>
    </div>
  )
}

export default FlowPage;

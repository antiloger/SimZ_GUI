import Flow from '@/components/default/ReactFlow/flow'
import PropertySheet from '@/components/default/ReactFlow/propertySheet';
import { ReactFlowProvider } from '@xyflow/react';

function FlowPage() {
  return (
    <div className='flex flex-col' >
      {/* <div> <MainMenubar /> </div> */}
      <div>
        <ReactFlowProvider>
          <Flow />
        </ReactFlowProvider>

        <PropertySheet />
      </div>
    </div>
  )
}

export default FlowPage;

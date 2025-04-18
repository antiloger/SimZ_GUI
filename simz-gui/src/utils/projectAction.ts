import { FlowState } from "@/states/flowState"
import { SimDataState } from "@/states/simDataState"
import { useSocketStore } from "./socketIo"
import { ErrorState } from "@/states/errorState"

export const SaveSimulationData = async () => {
  const { saveStateAsJson, saveGenStateAsJson, getProjectName } = SimDataState.getState()
  const { getJsonEdges, getJsonNodes } = FlowState.getState()

  const { save_data_state, save_flow_state } = useSocketStore.getState()
  const projectName = getProjectName()
  const state = saveStateAsJson()
  const genState = saveGenStateAsJson()
  const NodeData = getJsonNodes()
  const EdgeData = getJsonEdges()

  if (!projectName) {
    console.error('Project name is not set')
    return
  }

  if (!state) {
    console.error('State is not set')
    return
  }

  try {
    await save_data_state(projectName, state, genState)
    await save_flow_state(projectName, NodeData, EdgeData)
  } catch (error) {
    const { setError } = ErrorState.getState()
    setError({
      header: 'Error saving simulation',
      body: 'Failed to save simulation data. Please try again.',
    })
  }

  console.log('Simulation data saved successfully')
}

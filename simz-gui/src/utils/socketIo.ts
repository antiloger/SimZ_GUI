import { ErrorState } from '@/states/errorState';
import { FlowNode } from '@/states/flowState';
import { CompDataI, CompRegStore } from '@/types/component';
import { GenTypeState } from '@/types/configGen';
import { ProjectRowList } from '@/types/projects';
import { Edge } from '@xyflow/react';
import { io, Socket } from 'socket.io-client';
import { create } from 'zustand';

interface SocketStore {
  socket: Socket | null;
  connected: boolean;
  currentProject: string | null;

  connectSocket: () => void;
  disconnectSocket: () => void;
  ping: () => Promise<string | undefined>;
  get_project_list: () => Promise<ProjectRowList>
  create_new_project: (projectName: string, discription: string) => Promise<void>;
  get_registered_component: () => Promise<CompRegStore>;
  save_data_state: (projectName: string, state: { [id: string]: CompDataI }, genstate: GenTypeState) => Promise<void>;
  get_data_state: (projectName: string) => Promise<{ "state_data": { [id: string]: CompDataI }, "gen_data": GenTypeState }>;
  save_flow_state: (projectName: string, node: FlowNode[], edges: Edge[]) => Promise<void>;
  get_data_node: (projectName: string) => Promise<FlowNode[]>;
  get_data_edge: (projectName: string) => Promise<Edge[]>;
}

// Create socket connection utility
const CreateSocketConnection = () => {
  // Get environment variables or use defaults
  const socketUrl = 'http://localhost:5000';
  try {
    return io(socketUrl, {
      transports: ['websocket'],
      autoConnect: false,
      reconnectionAttempts: 2,
    });
  } catch (error) {
    console.error('Error creating socket connection:', error);
    throw new Error('Failed to create socket connection');
  }
};

export const useSocketStore = create<SocketStore>((set, get) => ({
  socket: null,
  connected: false,
  currentProject: null,

  connectSocket: () => {
    if (get().socket) {
      return;
    };

    const socket = CreateSocketConnection();

    socket.on('connect', () => {
      console.log('Connected to Socket.IO server');
      set({ connected: true });
    });

    socket.on('disconnect', () => {
      const { setError } = ErrorState.getState();
      console.log('Disconnected from Socket.IO server');
      setError({
        header: 'Socket Disconnected',
        body: 'The connection to the server has been lost. Please check your network connection and try again.',
        level: 'error'
      });
      set({ connected: false });
    });

    socket.on('connect_error', (error) => {
      const { setError } = ErrorState.getState();
      console.error('[ socketIO ] Connection error:', error);
      setError({
        header: 'Socket Connection Error',
        body: 'Failed to connect to the server. Please check your network connection and try again.',
      })
    });

    socket.connect();
    set({ socket });
  },

  disconnectSocket: () => {
    const { socket } = get();
    if (socket) {
      socket.disconnect();
      set({ socket: null, connected: false });
    }
  },

  ping: async () => {
    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first.",
      })
      return;
    }

    return new Promise<string>((resolve) => {
      socket.emit('ping', (response: string) => {
        resolve(response);
        console.log('>>> Ping successful', response);
      });
    });
  },

  get_project_list: async () => {
    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return {
        projects: [],
      };
    }

    return new Promise<ProjectRowList>((resolve) => {
      socket.emit('list_projects', {}, (response: any) => {
        console.log('>>> Project list response:', response);
        resolve(response);
      })
    })
  },

  create_new_project: async (projectName: string, discription: string) => {
    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return;
    }

    socket.emit('create_project', { "name": projectName, "discription": discription }, (response: any) => {
      if (response.error) {
        const { setError } = ErrorState.getState();
        console.error('[ socketIO ] Project creation error:', response.error);
        setError({
          header: 'response error',
          body: "project creation failed. please try again",
        })
      }
    });

    return;
  },

  get_registered_component: async () => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return {};

    }

    return new Promise<CompRegStore>((resolve) => {
      socket.emit('list_components', {}, (response: any) => {
        if (response.error) {
          const { setError } = ErrorState.getState();
          console.error('[ socketIO ] list component error :', response.error);
          setError({
            header: 'response error',
            body: "registered component list failed. please try again",
          })
        } else {
          console.log('>>> Registered component response:', response);
          resolve(response.components);
        }
      })
    })
  },

  save_data_state: async (projectName: string, state: { [id: string]: CompDataI }, genstate: GenTypeState) => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return;

    }

    socket.emit('save_state', { "project_name": projectName, "stateData": state, "genData": genstate }, (response: any) => {
      if (response.error) {
        const { setError } = ErrorState.getState();
        console.error('[ socketIO ] list component error :', response.error);
        setError({
          header: 'response error',
          body: "save data state failed. please try again",
        })
      }
    })
  },

  get_data_state: async (projectName: string) => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return {
        "state_data": {},
        "gen_data": {},
      };

    }

    return new Promise<{ "state_data": { [id: string]: CompDataI }, "gen_data": GenTypeState }>((resolve) => {
      socket.emit('get_state', { "project_name": projectName }, (response: any) => {
        if (response.error) {
          const { setError } = ErrorState.getState();
          console.error('[ socketIO ] list component error :', response.error);
          setError({
            header: 'response error',
            body: "get data state failed. please try again",
          })
        } else {
          console.log('>>> Registered component response:', response);
          resolve(response);
        }
      })
    })
  },

  save_flow_state: async (projectName: string, node: FlowNode[], edges: Edge[]) => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return;

    }

    socket.emit('save_node', { "project_name": projectName, "data": node }, (response: any) => {
      if (response.error) {
        const { setError } = ErrorState.getState();
        console.error('[ socketIO ] list component error :', response.error);
        setError({
          header: 'response error',
          body: "save data state failed. please try again",
        })
      }
    })


    socket.emit('save_edge', { "project_name": projectName, "data": edges }, (response: any) => {
      if (response.error) {
        const { setError } = ErrorState.getState();
        console.error('[ socketIO ] list component error :', response.error);
        setError({
          header: 'response error',
          body: "save data state failed. please try again",
        })
      }
    })
  },

  get_data_node: async (projectName: string) => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return [];

    }

    return new Promise<FlowNode[]>((resolve) => {
      socket.emit('get_node', { "project_name": projectName }, (response: any) => {
        if (response.error) {
          const { setError } = ErrorState.getState();
          console.error('[ socketIO ] list component error :', response.error);
          setError({
            header: 'response error',
            body: "get data state failed. please try again",
          })
        } else {
          console.log('>>> Registered component response:', response);
          resolve(response.data);
        }
      })
    })
  },

  get_data_edge: async (projectName: string) => {

    const { socket } = get();
    if (!socket) {
      const { setError } = ErrorState.getState();
      console.error('Socket is not connected');
      setError({
        header: 'Socket Not Connected',
        body: " socket is not connected. Please connect to the socket first",
      })
      return [];

    }

    return new Promise<Edge[]>((resolve) => {
      socket.emit('get_edge', { "project_name": projectName }, (response: any) => {
        if (response.error) {
          const { setError } = ErrorState.getState();
          console.error('[ socketIO ] list component error :', response.error);
          setError({
            header: 'response error',
            body: "get data state failed. please try again",
          })
        } else {
          console.log('>>> Registered component response:', response);
          resolve(response.data);
        }
      })
    })
  },
}));

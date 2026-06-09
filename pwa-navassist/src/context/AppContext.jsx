import React, { createContext, useContext, useReducer, useCallback } from 'react';

const initialState = {
  permissions: {
    camera: 'pending',
    microphone: 'pending',
    speaker: 'pending',
  },
  voice: {
    isListening: false,
    isSpeaking: false,
    isProcessing: false,
    status: 'idle',
    lastTranscript: '',
    lastResponse: '',
  },
  navigation: {
    isActive: false,
    from: null,
    to: null,
    route: [],
    currentStep: 0,
    currentPosition: null,
    totalDistance: 0,
    totalSteps: 0,
  },
  detection: {
    isActive: false,
    detectedObjects: [],
    fps: 0,
    lastAlert: null,
    modelLoaded: false,
  },
  ui: {
    activeTab: 'navigation',
    logs: [],
  },
  app: {
    initialized: false,
    error: null,
  },
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_PERMISSION':
      return {
        ...state,
        permissions: {
          ...state.permissions,
          [action.payload.key]: action.payload.value,
        },
      };

    case 'SET_VOICE_STATE':
      return {
        ...state,
        voice: { ...state.voice, ...action.payload },
      };

    case 'START_NAVIGATION':
      return {
        ...state,
        navigation: {
          ...state.navigation,
          isActive: true,
          from: action.payload.from,
          to: action.payload.to,
          route: action.payload.route,
          currentStep: 0,
          totalDistance: action.payload.totalDistance,
          totalSteps: action.payload.totalSteps,
        },
      };

    case 'UPDATE_NAVIGATION_STEP':
      return {
        ...state,
        navigation: {
          ...state.navigation,
          currentStep: action.payload,
        },
      };

    case 'SET_CURRENT_POSITION':
      return {
        ...state,
        navigation: {
          ...state.navigation,
          currentPosition: action.payload,
        },
      };

    case 'STOP_NAVIGATION':
      return {
        ...state,
        navigation: {
          ...initialState.navigation,
        },
      };

    case 'SET_DETECTION_ACTIVE':
      return {
        ...state,
        detection: {
          ...state.detection,
          isActive: action.payload,
        },
      };

    case 'UPDATE_DETECTION':
      return {
        ...state,
        detection: {
          ...state.detection,
          detectedObjects: action.payload.objects,
          fps: action.payload.fps,
        },
      };

    case 'SET_DETECTION_ALERT':
      return {
        ...state,
        detection: {
          ...state.detection,
          lastAlert: action.payload,
        },
      };

    case 'SET_MODEL_LOADED':
      return {
        ...state,
        detection: {
          ...state.detection,
          modelLoaded: action.payload,
        },
      };

    case 'SET_ACTIVE_TAB':
      return {
        ...state,
        ui: {
          ...state.ui,
          activeTab: action.payload,
        },
      };

    case 'ADD_LOG':
      return {
        ...state,
        ui: {
          ...state.ui,
          logs: [
            {
              id: Date.now(),
              timestamp: new Date().toISOString(),
              ...action.payload,
            },
            ...state.ui.logs.slice(0, 99),
          ],
        },
      };

    case 'SET_APP_INITIALIZED':
      return {
        ...state,
        app: {
          ...state.app,
          initialized: action.payload,
        },
      };

    case 'SET_ERROR':
      return {
        ...state,
        app: {
          ...state.app,
          error: action.payload,
        },
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        app: {
          ...state.app,
          error: null,
        },
      };

    default:
      return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const actions = {
    setPermission: useCallback((key, value) => {
      dispatch({ type: 'SET_PERMISSION', payload: { key, value } });
    }, []),

    setVoiceState: useCallback((payload) => {
      dispatch({ type: 'SET_VOICE_STATE', payload });
    }, []),

    startNavigation: useCallback((payload) => {
      dispatch({ type: 'START_NAVIGATION', payload });
    }, []),

    updateNavigationStep: useCallback((step) => {
      dispatch({ type: 'UPDATE_NAVIGATION_STEP', payload: step });
    }, []),

    setCurrentPosition: useCallback((position) => {
      dispatch({ type: 'SET_CURRENT_POSITION', payload: position });
    }, []),

    stopNavigation: useCallback(() => {
      dispatch({ type: 'STOP_NAVIGATION' });
    }, []),

    setDetectionActive: useCallback((active) => {
      dispatch({ type: 'SET_DETECTION_ACTIVE', payload: active });
    }, []),

    updateDetection: useCallback((payload) => {
      dispatch({ type: 'UPDATE_DETECTION', payload });
    }, []),

    setDetectionAlert: useCallback((alert) => {
      dispatch({ type: 'SET_DETECTION_ALERT', payload: alert });
    }, []),

    setModelLoaded: useCallback((loaded) => {
      dispatch({ type: 'SET_MODEL_LOADED', payload: loaded });
    }, []),

    setActiveTab: useCallback((tab) => {
      dispatch({ type: 'SET_ACTIVE_TAB', payload: tab });
    }, []),

    addLog: useCallback((payload) => {
      dispatch({ type: 'ADD_LOG', payload });
    }, []),

    setAppInitialized: useCallback((initialized) => {
      dispatch({ type: 'SET_APP_INITIALIZED', payload: initialized });
    }, []),

    setError: useCallback((error) => {
      dispatch({ type: 'SET_ERROR', payload: error });
    }, []),

    clearError: useCallback(() => {
      dispatch({ type: 'CLEAR_ERROR' });
    }, []),
  };

  return (
    <AppContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppState must be used within AppProvider');
  }
  return context;
}

export { initialState };

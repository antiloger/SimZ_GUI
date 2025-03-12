import { ConfigGenerator } from "./component";

export interface TimeStepGenConfig {
  intervalTime: number;
  noItem: number;
  isIntervalTimeRandom: boolean;
  IntervalTimeRandom: {
    from: number;
    to: number;
  };
  timePerNoItem: number;
  isTimePerNoItemRandom: boolean;
  TimePerNoItemRandom: {
    from: number;
    to: number;
  };
}

export const NewTimeStepGenConfigFn = () => {
  const config: TimeStepGenConfig = {
    intervalTime: 0,
    noItem: 0,
    isIntervalTimeRandom: false,
    IntervalTimeRandom: {
      from: 0,
      to: 0,
    },
    timePerNoItem: 0,
    isTimePerNoItemRandom: false,
    TimePerNoItemRandom: {
      from: 0,
      to: 0,
    },
  };
  const configFn: ConfigGenerator = {
    genFn: "timestep",
    config: config
  }
  return configFn
};

export interface GenAttributes {
  type: string;
  value: string | number | boolean | object | null;
}

export interface GenTypes {
  typeName: string;
  genComponentId: string;
  attributes: { [attr: string]: GenAttributes };
}

export interface GenTypeState {
  [type: string]: GenTypes;
}

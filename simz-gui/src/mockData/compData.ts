import { CompDataI, CompRegStore } from "@/types/component";

// Component Registry Store (CompRegStore)
export const componentRegStore: CompRegStore = {
  generator: {
    DataGenerator: {
      typeName: "DataGenerator",
      description: "Generates sample data streams",
      category: "generator",
      color: "#4CAF50",
      InputForm: [
        {
          inputName: "frequency",
          fieldType: "number",
          defaultValue: 60,
          validation: "",
          display: true,
          required: true
        },
        {
          inputName: "dataType",
          fieldType: "select",
          defaultValue: "random",
          validation: "",
          display: true,
          description: "Type of data to generate",
          required: true,
          options: ["random", "sequential", "pattern"]
        },
        {
          inputName: "active",
          fieldType: "checkbox",
          defaultValue: true,
          validation: "",
          display: false,
          required: false
        }
      ],
      OutputData: [{ typeOut: "Table" }]
    }
  },
  model: {
    RegressionModel: {
      typeName: "RegressionModel",
      description: "Linear regression predictive model",
      category: "model",
      color: "#2196F3",
      InputForm: [
        {
          inputName: "learningRate",
          fieldType: "number",
          defaultValue: 0.01,
          validation: "",
          display: true,
          required: true
        },
        {
          inputName: "features",
          fieldType: "multiselect",
          defaultValue: ["age", "income"],
          validation: "",
          display: true,
          options: ["age", "income", "location", "gender"],
          required: true
        }
      ],
      OutputData: [{ typeOut: "Chart-Pie" }, { typeOut: "Table" }]
    }
  },
  distributer: {
    DataDistributor: {
      typeName: "DataDistributor",
      description: "Distributes data to multiple endpoints",
      category: "distributer",
      color: "#9C27B0",
      InputForm: [
        {
          inputName: "targets",
          fieldType: "multiselect",
          defaultValue: ["cloud", "local"],
          validation: "",
          display: true,
          options: ["cloud", "local", "api"],
          required: true
        }
      ],
      OutputData: [{ typeOut: "Card" }]
    }
  }
};

// Component Data Instances (CompDataI)
export const componentData: { [id: string]: CompDataI } = {
  "comp-1234": {
    id: "comp-1234",
    compName: "Main Data Generator",
    typeName: "DataGenerator",
    category: "generator",
    color: "#4CAF50",
    inputData: {
      frequency: 60,
      dataType: "random",
      active: true
    },
    inputConn: [],
    outpuConn: [
      {
        from: "comp-1234",
        type: ["data-stream"],
        validation: "format:json"
      }
    ],
    Runners: [
      {
        type: "PreFunc",
        name: "normalize-data",
        args: ["input_stream", { threshold: 0.5 }]
      }
    ]
  },
  "comp-5678": {
    id: "comp-5678",
    compName: "Customer Prediction Model",
    typeName: "RegressionModel",
    category: "model",
    color: "#2196F3",
    inputData: {
      learningRate: 0.05,
      features: ["age", "income", "location"]
    },
    inputConn: [
      {
        from: "comp-1234",
        type: ["data-stream"],
        validation: "format:json"
      }
    ],
    outpuConn: [
      {
        from: "comp-5678",
        type: ["prediction-result"],
        validation: "schema:v2"
      }
    ],
    Runners: [
      {
        type: "ML",
        name: "linear-regression",
        args: ["input_data", { iterations: 1000 }]
      }
    ]
  }
};

import { RunnerFile } from "@/types/component";

export const initialRunnerFile: RunnerFile = {
  run: `
# u must return input if not the resource process not gonna work
def main():
    print("Running main application")
    
if __name__ == "__main__":
    main()`,
  generator: `def generate_data():
    print("Generating data...")
    return {"status": "success"}`,
  model: `class Model:
    def __init__(self):
        self.name = "Default Model"
        
    def train(self, data):
        print(f"Training {self.name} with data")
        
    def predict(self, input_data):
        return "Prediction result"`,
  event: `# Event handling functions

def process_event(event_data):
    print("Processing event data")
    return event_data`,
}

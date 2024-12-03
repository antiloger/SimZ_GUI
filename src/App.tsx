import { useState } from "react";
import "./App.css";
import { Button } from "./components/ui/button";
import ReactFw from "./components/default/reactflow";

function App() {
  let [isBtn, setBtn] = useState("hello")

  function btnclied() {
    setBtn("btn clicked")
  }

  return (
    <main>
      <div className="flex flex-col bg-slate-100 gap-y-5 items-center justify-center " >
        <h1 className="text-red-500 text-3xl" > Hello Tauri, {isBtn} </h1>
        <Button onClick={() => btnclied()} >Submit</Button>
        <div >
          <ReactFw />
        </div>
      </div>
    </main>
  );
}

export default App;

"""
Fixed mixer function for the simulation.
"""

from collections import deque

def mixer(ctx, item):
    """
    Mixer function that processes water and chlorine items.
    
    Args:
        ctx: The component context (self reference from the component)
        item: The GenContainer to process
        
    Returns:
        GenContainer: The processed container or None if no output
    """
    # Get timeouts from component variables
    pt = int(ctx.var.get("p_timeout"))  # Default to 1 if not set
    gt = int(ctx.var.get("g_timeout"))  # Default to 2 if not set
    print("[output] >> test")
    # Wait for processing timeout
    yield ctx.env.timeout(pt)
    
    # Get the hold queues from component variables
    # Initialize them if they don't exist
    if ctx.var.get("c_hold") is None:
        ctx.var.set("c_hold", deque())
    if ctx.var.get("w_hold") is None:
        ctx.var.set("w_hold", deque())
        
    c_hold = ctx.var.get("c_hold")
    w_hold = ctx.var.get("w_hold")
    print(f"[output] >> {c_hold}")
    
    # Process based on item type
    if item.checkType("water"):
        # If we have chlorine items waiting
        if c_hold and len(c_hold) > 0:
            # Get a chlorine item
            chlorine_item = c_hold.pop()
            if chlorine_item is not None and chlorine_item.checkType("chlorine"):
                # Mix water and chlorine
                yield ctx.env.timeout(gt)
                
                # Create a mixed water container
                mixed_water = ctx.create_container("mixed_water", {
                    "clean": ctx.random(70, 85),
                    "amount": ctx.random(7, 10)
                })
                
                # Log the mixing event
                ctx.log_event(
                    action="MIX",
                    values={
                        "water_id": item.containerId,
                        "chlorine_id": chlorine_item.containerId,
                        "time": ctx.env.now,
                    },
                    PDV=mixed_water.Display(),
                )
                
                return mixed_water
            else:
                # If not a valid chlorine item, put it back
                if chlorine_item is not None:
                    c_hold.append(chlorine_item)
                # Store the water item for later
                w_hold.append(item)
                return None
        else:
            # No chlorine available, store water for later
            w_hold.append(item)
            return None
            
    elif item.checkType("chlorine"):
        # If we have water items waiting
        if w_hold and len(w_hold) > 0:
            # Get a water item
            water_item = w_hold.pop()
            if water_item is not None and water_item.checkType("water"):
                # Mix water and chlorine
                yield ctx.env.timeout(gt)
                
                # Create a mixed water container
                mixed_water = ctx.create_container("mixed_water", {
                    "clean": ctx.random(70, 85),
                    "amount": ctx.random(7, 10)
                })
                
                # Log the mixing event
                ctx.log_event(
                    action="MIX",
                    values={
                        "water_id": water_item.containerId,
                        "chlorine_id": item.containerId,
                        "time": ctx.env.now,
                    },
                    PDV=mixed_water.Display(),
                )
                
                return mixed_water
            else:
                # If not a valid water item, put it back
                if water_item is not None:
                    w_hold.append(water_item)
                # Store the chlorine item for later
                c_hold.append(item)
                return None
        else:
            # No water available, store chlorine for later
            c_hold.append(item)
            return None
    else:
        # Unknown item type, just pass it through
        return item

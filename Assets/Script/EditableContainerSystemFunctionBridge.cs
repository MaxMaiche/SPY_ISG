using UnityEngine;

public class EditableContainerSystemFunctionBridge : MonoBehaviour
{
	public void resetScriptContainer(GameObject scriptContainer)
	{
		EditableContainerSystemFunction.instance.resetScriptContainer(scriptContainer);
	}

	public void removeContainer()
	{
		EditableContainerSystemFunction.instance.removeContainer(gameObject, false);
	}

	public void newNameContainer(string name)
	{
		EditableContainerSystemFunction.instance.newNameContainer(name);
	}

	public void selectContainer(UIRootContainer container)
	{
		EditableContainerSystemFunction.instance.selectContainer(container);
	}
}

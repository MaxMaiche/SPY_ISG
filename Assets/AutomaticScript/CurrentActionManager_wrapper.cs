using UnityEngine;
using FYFY;

public class CurrentActionManager_wrapper : BaseWrapper
{
	public UnityEngine.GameObject functionContainerPrefab;
	private void Start()
	{
		this.hideFlags = HideFlags.NotEditable;
		MainLoop.initAppropriateSystemField (system, "functionContainerPrefab", functionContainerPrefab);
	}

}

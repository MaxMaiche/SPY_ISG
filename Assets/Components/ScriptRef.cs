using UnityEngine;

public class ScriptRef : MonoBehaviour {
	// Advice: FYFY component aims to contain only public members (according to Entity-Component-System paradigm).
	public GameObject executableScript;
	public GameObject executableFunction;	
	public GameObject executablePanel; //container to show/hide - root of Container prefab
	public GameObject executableFunctionPanel; //container to show/hide - root of Container prefab
	public GameObject biblioFunction; // Contain all functions
	public bool inFunction;
	public GameObject currentFunctionBlock;
	public bool scriptFinished;
	public int nbOfInactions;
}
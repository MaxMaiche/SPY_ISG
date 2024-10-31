using UnityEngine;

public class Function : BaseElement {
	// Advice: FYFY component aims to contain only public members (according to Entity-Component-System paradigm).
    public enum ActionType { Function };
    public ActionType actionType;
    public string functionName;
}
﻿using UnityEngine;
using System.Collections.Generic;

public class AddSpecificContainerFunction : MonoBehaviour {
	public string title = "";
	public UIRootContainer.EditMode editState = UIRootContainer.EditMode.Editable;
	public UIRootContainer.SolutionType typeState = UIRootContainer.SolutionType.Undefined;
	public List<GameObject> script = null;
}
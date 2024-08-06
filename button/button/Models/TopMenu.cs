using System;
using System.Collections.Generic;

namespace button.Models;

public partial class TopMenu
{
    public int ClickID { get; set; }

    public string? ButtonType { get; set; }

    public DateTime? ClickTime { get; set; }

    public int? Sum { get; set; }
}

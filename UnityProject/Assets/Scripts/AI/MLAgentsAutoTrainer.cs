#region Includes
using UnityEngine;
using System.Diagnostics;
using System.IO;
#endregion

public class MLAgentsAutoTrainer : MonoBehaviour
{
    #region Members
    
    [Header("Training Configuration")]
    [SerializeField]
    private bool autoStartTraining = true;
    
    [SerializeField]
    private string configPath = "config/car_racing_config.yaml";
    
    [SerializeField]
    private string runId = "car_racing_ppo";
    
    [Header("Python Configuration")]
    [SerializeField]
    private string pythonPath = "python";
    
    [SerializeField]
    private string trainingScriptPath = "../python/train_car_mlagents.py";
    
    private Process trainingProcess;
    private bool trainingStarted = false;
    
    #endregion
    
    #region Unity Methods
    
    void Start()
    {
        if (autoStartTraining && !trainingStarted)
        {
            StartTraining();
        }
    }
    
    void OnDestroy()
    {
        StopTraining();
    }
    
    void OnApplicationQuit()
    {
        StopTraining();
    }
    
    #endregion
    
    #region Training Methods
    
    public void StartTraining()
    {
        if (trainingStarted)
        {
            UnityEngine.Debug.LogWarning("ML-Agents training is already running.");
            return;
        }
        
        string projectRoot = Application.dataPath.Replace("/Assets", "");
        string scriptPath = Path.Combine(projectRoot, trainingScriptPath.Replace("../", ""));
        
        if (!File.Exists(scriptPath))
        {
            UnityEngine.Debug.LogError($"Training script not found at: {scriptPath}");
            UnityEngine.Debug.LogError("Please make sure the path is correct or start training manually.");
            return;
        }
        
        string pythonDir = Path.GetDirectoryName(scriptPath);
        
        try
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = pythonPath,
                Arguments = $"\"{scriptPath}\"",
                WorkingDirectory = pythonDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = false
            };
            
            startInfo.EnvironmentVariables["MLAGENTS_AUTO_MODE"] = "true";
            
            trainingProcess = Process.Start(startInfo);
            trainingStarted = true;
            
            if (trainingProcess != null)
            {
                trainingProcess.BeginOutputReadLine();
                trainingProcess.BeginErrorReadLine();
            }
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError($"Failed to start training process: {e.Message}");
            UnityEngine.Debug.LogError("You may need to:");
            UnityEngine.Debug.LogError("1. Install ML-Agents: pip install mlagents");
            UnityEngine.Debug.LogError("2. Start training manually: python train_car_mlagents.py");
        }
    }
    
    public void StopTraining()
    {
        if (trainingProcess != null && !trainingProcess.HasExited)
        {
            UnityEngine.Debug.Log("Stopping ML-Agents training process...");
            try
            {
                trainingProcess.Kill();
                trainingProcess.WaitForExit(2000);
            }
            catch (System.Exception e)
            {
                UnityEngine.Debug.LogWarning($"Error stopping training process: {e.Message}");
            }
            finally
            {
                trainingProcess.Dispose();
                trainingProcess = null;
                trainingStarted = false;
            }
        }
    }
    
    #endregion
}

